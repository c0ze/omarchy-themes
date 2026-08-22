import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import QtQuick
import qs.Commons

// Drifting fog over the wallpaper.
//
// A theme opts in by shipping a fog/ directory holding plates plus a fog.json;
// a theme without one costs nothing at all, because the layer model stays empty
// and no animation is ever created.
//
// This is a plugin of its own rather than a fork of omarchy.background, so the
// stock background renderer keeps updating normally and a mistake here cannot
// leave the desktop black. It sits on WlrLayer.Bottom: above the Background
// layer the wallpaper uses, below ordinary windows. The surface is masked to an
// empty input region, so clicks fall through to the wallpaper as usual.
//
// The timings are ported from pagan.tr's fog.css. Movement and opacity run on
// deliberately unrelated periods (15s/13s against 10s/21s); the beat between
// them is what reads as swirling rather than sliding.
Item {
  id: root

  property var fogPlates: []
  property real fogIntensity: 0
  property string fogProfile: "fog"

  readonly property var fogProfiles: ({
    "fog": [
      { plate: 0, move: 15000, cycle: 10000, stops: [0.10, 0.50, 0.28, 0.40, 0.16], at: [0, 0.22, 0.40, 0.58, 0.80] },
      { plate: 1, move: 13000, cycle: 21000, stops: [0.50, 0.20, 0.10, 0.30], at: [0, 0.25, 0.50, 0.80] },
      { plate: 1, move: 13000, cycle: 21000, stops: [0.80, 0.20, 0.60, 0.30], at: [0, 0.27, 0.52, 0.68] }
    ],
    // Light grounds get two slower layers, matching the site's mist variant.
    // Their plates ship pre-inverted, so the fog is dark rather than luminous.
    "mist": [
      { plate: 0, move: 20000, cycle: 12000, stops: [0.28, 0.56, 0.42, 0.49], at: [0, 0.25, 0.50, 0.75] },
      { plate: 1, move: 25000, cycle: 18000, stops: [0.30, 0.24, 0.42], at: [0, 0.30, 0.60] }
    ]
  })

  readonly property var fogLayers: {
    if (!fogPlates || fogPlates.length === 0 || fogIntensity <= 0) return []
    var spec = fogProfiles[fogProfile] || fogProfiles["fog"]
    var out = []
    for (var i = 0; i < spec.length; i++) {
      var layer = spec[i]
      if (layer.plate >= fogPlates.length) continue
      out.push({ src: fogPlates[layer.plate], move: layer.move, cycle: layer.cycle,
                 stops: layer.stops, at: layer.at, phase: i / spec.length })
    }
    return out
  }

  // Piecewise-linear across the opacity stops, wrapping the last segment back to
  // the first: exactly how a CSS keyframe set with matching 0% and 100% behaves.
  function fogOpacityAt(stops, at, t) {
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
      '  d="$base/fog"; [[ -d $d ]] || continue',
      '  intensity=0.45; profile=fog',
      '  if [[ -f $d/fog.json ]]; then',
      // jq takes a bare filter as one argv element. Do not quote it: escaped
      // quotes inside this QML string collapse and silently break the filter.
      '    v=$(jq -r .intensity "$d/fog.json" 2>/dev/null); [[ -n $v && $v != null ]] && intensity=$v',
      '    v=$(jq -r .profile "$d/fog.json" 2>/dev/null); [[ -n $v && $v != null ]] && profile=$v',
      '  fi',
      '  echo "$intensity"; echo "$profile"; ls "$d"/*.png 2>/dev/null; break',
      'done'
    ].join("\n")]
    stdout: StdioCollector {
      onStreamFinished: {
        var lines = String(text || "").trim().split("\n").filter(function(l) { return l.length > 0 })
        if (lines.length < 3) {
          root.fogIntensity = 0
          root.fogPlates = []
          console.log("gand fog: none for this theme")
          return
        }
        root.fogIntensity = parseFloat(lines[0]) || 0
        root.fogProfile = lines[1]
        root.fogPlates = lines.slice(2).map(function(p) { return Util.fileUrl(p) })
        console.log("gand fog:", root.fogProfile, "intensity=" + root.fogIntensity,
                    "plates=" + root.fogPlates.length, "layers=" + root.fogLayers.length)
      }
    }
  }

  // The theme slug is what decides which plates apply, so watch the file
  // omarchy writes it to rather than polling or hooking the background IPC.
  FileView {
    path: Quickshell.env("HOME") + "/.local/state/omarchy/current/theme.name"
    watchChanges: true
    onFileChanged: reload()
    onLoaded: root.refresh()
  }

  IpcHandler {
    target: "fog"

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
      visible: root.fogLayers.length > 0

      WlrLayershell.namespace: "gand-fog"
      WlrLayershell.layer: WlrLayer.Bottom
      WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
      exclusionMode: ExclusionMode.Ignore

      // Input falls straight through to the wallpaper below.
      mask: Region {}

      Item {
        id: fogWrapper
        anchors.fill: parent
        clip: true
        opacity: root.fogIntensity

        Repeater {
          model: root.fogLayers

          // Two copies of the plate side by side, sliding left by exactly one
          // copy width and looping. The wrap is seamless because the second
          // copy has arrived precisely where the first one started.
          delegate: Item {
            id: fogLayer
            required property var modelData

            property real cyclePhase: 0

            width: panel.width * 2
            height: panel.height
            opacity: root.fogOpacityAt(modelData.stops, modelData.at,
                                       (cyclePhase + modelData.phase) % 1)

            Image {
              x: 0
              width: panel.width
              height: panel.height
              source: fogLayer.modelData.src
              fillMode: Image.PreserveAspectCrop
              asynchronous: true
              cache: true
              smooth: true
              mipmap: true
            }

            Image {
              x: panel.width
              width: panel.width
              height: panel.height
              source: fogLayer.modelData.src
              fillMode: Image.PreserveAspectCrop
              asynchronous: true
              cache: true
              smooth: true
              mipmap: true
            }

            NumberAnimation on x {
              running: panel.visible
              loops: Animation.Infinite
              from: 0
              to: -panel.width
              duration: fogLayer.modelData.move
              easing.type: Easing.Linear
            }

            NumberAnimation on cyclePhase {
              running: panel.visible
              loops: Animation.Infinite
              from: 0
              to: 1
              duration: fogLayer.modelData.cycle
              easing.type: Easing.Linear
            }
          }
        }
      }
    }
  }
}
