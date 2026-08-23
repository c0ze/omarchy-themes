import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import QtQuick
import qs.Commons

// Animated backdrop over the wallpaper.
//
// A theme opts in by shipping a backdrop/ directory holding plates plus a
// backdrop.json naming a profile and an intensity. Themes without one cost
// nothing at all: the layer model stays empty and no animation is created.
//
// Two kinds of motion, because two families want different things:
//
//   drift  plates slide sideways, two copies each so the wrap is seamless.
//          Pagan's fog and mist -- ported from pagan.tr's fog.css, movement and
//          opacity on unrelated periods (15s/13s against 10s/21s) so the beat
//          reads as swirling rather than sliding.
//   spin   plates rotate about the screen centre at different rates and in
//          opposing directions. Gand's orrery: its mark is an astronomical
//          device, so its rings turn rather than drift.
//
// This is a plugin of its own rather than a fork of omarchy.background, so the
// stock renderer keeps updating normally and a mistake here cannot leave the
// desktop black. It sits on WlrLayer.Bottom -- above the wallpaper, below
// ordinary windows -- masked to an empty input region so clicks fall through.
Item {
  id: root

  property var plates: []
  property real intensity: 0
  property string profile: "fog"
  property real speed: 1

  readonly property var profiles: ({
    "fog": {
      kind: "drift",
      layers: [
        { plate: 0, move: 15000, cycle: 10000, stops: [0.10, 0.50, 0.28, 0.40, 0.16], at: [0, 0.22, 0.40, 0.58, 0.80] },
        { plate: 1, move: 13000, cycle: 21000, stops: [0.50, 0.20, 0.10, 0.30], at: [0, 0.25, 0.50, 0.80] },
        { plate: 1, move: 13000, cycle: 21000, stops: [0.80, 0.20, 0.60, 0.30], at: [0, 0.27, 0.52, 0.68] }
      ]
    },
    "mist": {
      kind: "drift",
      layers: [
        { plate: 0, move: 20000, cycle: 12000, stops: [0.28, 0.56, 0.42, 0.49], at: [0, 0.25, 0.50, 0.75] },
        { plate: 1, move: 25000, cycle: 18000, stops: [0.30, 0.24, 0.42], at: [0, 0.30, 0.60] }
      ]
    },
    // Periods are minutes, not seconds. An orrery that visibly turns is a
    // fidget; this should only be noticeable if you sit and watch it.
    "orrery": {
      kind: "spin",
      layers: [
        { plate: 0, period: 420000, dir: 1, scale: 1.00, cycle: 47000, stops: [0.62, 0.90, 0.70], at: [0, 0.35, 0.70] },
        { plate: 1, period: 300000, dir: -1, scale: 1.00, cycle: 31000, stops: [0.90, 0.62, 0.80], at: [0, 0.30, 0.65] },
        { plate: 2, period: 540000, dir: 1, scale: 1.00, cycle: 39000, stops: [0.75, 0.95, 0.68], at: [0, 0.40, 0.75] }
      ]
    }
  })

  readonly property var layers: {
    if (!plates || plates.length === 0 || intensity <= 0) return []
    var spec = profiles[profile] || profiles["fog"]
    var out = []
    for (var i = 0; i < spec.layers.length; i++) {
      var layer = spec.layers[i]
      if (layer.plate >= plates.length) continue
      var entry = {}
      for (var k in layer) entry[k] = layer[k]
      entry.src = plates[layer.plate]
      entry.kind = spec.kind
      // speed > 1 is faster; guard against a zero or negative in the json.
      var rate = speed > 0 ? speed : 1
      if (entry.move) entry.move = Math.round(entry.move / rate)
      if (entry.period) entry.period = Math.round(entry.period / rate)
      entry.phase = i / spec.layers.length
      out.push(entry)
    }
    return out
  }

  readonly property bool drifting: layers.length > 0 && layers[0].kind === "drift"

  // Piecewise-linear across the opacity stops, wrapping the last segment back
  // to the first: how a CSS keyframe set with matching 0% and 100% behaves.
  function opacityAt(stops, at, t) {
    var n = stops.length
    for (var i = n - 1; i >= 0; i--) {
      if (t >= at[i]) {
        var t0 = at[i]
        var v0 = stops[i]
        var t1 = (i + 1 < n) ? at[i + 1] : 1.0
        var v1 = (i + 1 < n) ? stops[i + 1] : stops[0]
        var f = (t1 > t0) ? (t - t0) / (t1 - t0) : 0
        return v0 + (v1 - v0) * f
      }
    }
    return stops[0]
  }

  function refresh() {
    if (!resolveProc.running) resolveProc.running = true
  }

  // Resolve plates through the theme's own directory, not the current/theme
  // state copy: that path is identical for every theme, so Qt would keep
  // serving the first theme's cached plates.
  Process {
    id: resolveProc
    command: ["bash", "-c", [
      'name=$(cat "$HOME/.local/state/omarchy/current/theme.name" 2>/dev/null)',
      '[[ -n $name ]] || exit 0',
      'for base in "$HOME/.config/omarchy/themes/$name" "$HOME/.local/share/omarchy/themes/$name"; do',
      '  d="$base/backdrop"; [[ -d $d ]] || continue',
      '  intensity=0.20; profile=fog; speed=1',
      // jq takes a bare filter as one argv element. Do not quote it: escaped
      // quotes inside this QML string collapse and silently break the filter.
      '  if [[ -f $d/backdrop.json ]]; then',
      '    v=$(jq -r .intensity "$d/backdrop.json" 2>/dev/null); [[ -n $v && $v != null ]] && intensity=$v',
      '    v=$(jq -r .profile "$d/backdrop.json" 2>/dev/null); [[ -n $v && $v != null ]] && profile=$v',
      '    v=$(jq -r .speed "$d/backdrop.json" 2>/dev/null); [[ -n $v && $v != null ]] && speed=$v',
      '  fi',
      '  echo "$intensity"; echo "$profile"; echo "$speed"; ls "$d"/*.png 2>/dev/null; break',
      'done'
    ].join("\n")]
    stdout: StdioCollector {
      onStreamFinished: {
        var lines = String(text || "").trim().split("\n").filter(function(l) { return l.length > 0 })
        if (lines.length < 4) {
          root.intensity = 0
          root.plates = []
          root.speed = 1
          console.log("gand backdrop: none for this theme")
          return
        }
        root.intensity = parseFloat(lines[0]) || 0
        root.profile = lines[1]
        root.speed = parseFloat(lines[2]) || 1
        root.plates = lines.slice(3).map(function(p) { return Util.fileUrl(p) })
        console.log("gand backdrop:", root.profile, "intensity=" + root.intensity,
                    "speed=" + root.speed, "plates=" + root.plates.length,
                    "layers=" + root.layers.length)
      }
    }
  }

  // The theme slug decides which plates apply, so watch the file omarchy writes
  // it to rather than polling or hooking the background IPC.
  FileView {
    path: Quickshell.env("HOME") + "/.local/state/omarchy/current/theme.name"
    watchChanges: true
    onFileChanged: reload()
    onLoaded: root.refresh()
  }

  IpcHandler {
    target: "backdrop"

    function refresh(): void {
      root.refresh()
    }
  }

  Component.onCompleted: refresh()

  Variants {
    model: Quickshell.screens

    PanelWindow {
      id: panel
      required property var modelData

      screen: modelData
      anchors { top: true; bottom: true; left: true; right: true }
      color: "transparent"
      visible: root.layers.length > 0

      WlrLayershell.namespace: "gand-backdrop"
      WlrLayershell.layer: WlrLayer.Bottom
      WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
      exclusionMode: ExclusionMode.Ignore

      // Input falls straight through to the wallpaper below.
      mask: Region {}

      readonly property real side: Math.max(width, height) * 1.05

      Item {
        anchors.fill: parent
        clip: true
        opacity: root.intensity

        Repeater {
          model: root.layers

          delegate: Item {
            id: layer
            required property var modelData

            property real cyclePhase: 0
            property real spin: 0
            // Animated separately from x: a `NumberAnimation on x` takes the
            // property over as a value source even while stopped, which would
            // destroy the centring binding that spin layers need.
            property real driftX: 0

            readonly property bool drift: modelData.kind === "drift"

            // Drift lays two copies side by side and slides one width; spin
            // squares up on the screen centre and turns.
            width: drift ? panel.width * 2 : panel.side * (modelData.scale || 1)
            height: drift ? panel.height : width
            x: drift ? driftX : (panel.width - width) / 2
            y: drift ? 0 : (panel.height - height) / 2

            opacity: root.opacityAt(modelData.stops, modelData.at,
                                    (cyclePhase + modelData.phase) % 1)

            transform: Rotation {
              origin.x: layer.width / 2
              origin.y: layer.height / 2
              angle: layer.drift ? 0 : layer.spin
            }

            Image {
              x: 0
              width: layer.drift ? panel.width : layer.width
              height: layer.drift ? panel.height : layer.height
              source: layer.modelData.src
              fillMode: layer.drift ? Image.PreserveAspectCrop : Image.PreserveAspectFit
              asynchronous: true
              cache: true
              smooth: true
              mipmap: true
            }

            // Second copy, drift only: it arrives exactly where the first
            // started, so the wrap is seamless.
            Image {
              visible: layer.drift
              x: panel.width
              width: panel.width
              height: panel.height
              source: layer.drift ? layer.modelData.src : ""
              fillMode: Image.PreserveAspectCrop
              asynchronous: true
              cache: true
              smooth: true
              mipmap: true
            }

            NumberAnimation on driftX {
              running: panel.visible && layer.drift
              loops: Animation.Infinite
              from: 0
              to: -panel.width
              duration: layer.modelData.move || 1
              easing.type: Easing.Linear
            }

            NumberAnimation on spin {
              running: panel.visible && !layer.drift
              loops: Animation.Infinite
              from: 0
              to: 360 * (layer.modelData.dir || 1)
              duration: layer.modelData.period || 1
              easing.type: Easing.Linear
            }

            NumberAnimation on cyclePhase {
              running: panel.visible
              loops: Animation.Infinite
              from: 0
              to: 1
              duration: layer.modelData.cycle
              easing.type: Easing.Linear
            }
          }
        }
      }
    }
  }
}
