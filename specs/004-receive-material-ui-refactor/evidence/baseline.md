# Baseline — Spec 004

Captured: 2026-11-19T14:14:39Z at HEAD `1fb8ef8`

## git status --porcelain

```text
 M .specify/scripts/python/__pycache__/common.cpython-315.pyc
?? specs/004-receive-material-ui-refactor/
```

## git diff --stat

```text
 .../python/__pycache__/common.cpython-315.pyc       | Bin 36453 -> 36439 bytes
 1 file changed, 0 insertions(+), 0 deletions(-)
```

Unrelated pre-existing changes (.specify/*, tag-provider and translations config) are left untouched by this feature.

## Schedule action panel reference values (T002)

Source: `services/ignition/projects/kanoaMES/com.inductiveautomation.perspective/views/training/receivingOrdersSchedule/view.json`

```json
{
  "root.props": {
    "direction": "column",
    "style": {
      "gap": "2px",
      "padding": "3px"
    }
  },
  "flxMain": {
    "props": {
      "style": {
        "gap": "3px"
      }
    },
    "position": {
      "grow": 1
    }
  },
  "flxActions": {
    "props": {
      "justify": "center",
      "style": {
        "classes": "kanoa/container",
        "minWidth": "35px",
        "overflow": "hidden"
      }
    },
    "position": {
      "shrink": 0
    }
  },
  "flxAction": {
    "props": {
      "alignItems": "center",
      "direction": "column",
      "style": {
        "gap": "5px",
        "padding": "5px"
      }
    },
    "position": {
      "basis": "40px",
      "shrink": 0
    }
  },
  "btnConfirm": {
    "props": {
      "image": {
        "icon": {
          "path": "material/check_circle_outline"
        }
      },
      "style": {
        "classes": "kanoa/button/flatIcon",
        "width": "30px"
      },
      "text": ""
    },
    "position": {
      "basis": "30px",
      "shrink": 0
    }
  }
}
```
