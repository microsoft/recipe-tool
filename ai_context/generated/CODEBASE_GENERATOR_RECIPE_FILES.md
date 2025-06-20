# recipes/codebase_generator

[collect-files]

**Search:** ['recipes/codebase_generator']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
**Include:** []
**Date:** 6/18/2025, 12:10:57 PM
**Files:** 8

=== File: recipes/codebase_generator/README.md ===
# Codebase Generator

Recipes for generating code from blueprints - demonstrates self-generating capability.

## Quick Examples

```bash
# Generate all Recipe Executor code
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json

# Generate specific component
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json \
   component_id=steps.llm_generate
```

See blueprint files in `blueprints/recipe_executor/` for component definitions.


=== File: recipes/codebase_generator/codebase_generator_recipe.json ===
{
  "steps": [
    {
      "type": "set_context",
      "config": {
        "key": "project_blueprints_root",
        "value": "{{ project_blueprints_root | default: 'blueprints/recipe_executor' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "component_id",
        "value": "{{ component_id | default: 'all' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "model",
        "value": "{{ model | default: 'openai/o4-mini' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "output_root",
        "value": "{{ output_root | default: 'output' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "refs_root",
        "value": "{{ refs_root | default: 'ai_context' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "existing_code_root",
        "value": "{{ existing_code_root | default: 'recipe-executor/recipe_executor' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "output_path",
        "value": "{{ output_path | default: '' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "dev_guide_path",
        "value": "{{ dev_guide_path | default: 'ai_context/DEV_GUIDE_FOR_PYTHON.md' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "edit",
        "value": "{{ edit | default: false }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "recipe_root",
        "value": "{{ recipe_root | default: 'recipes/codebase_generator' }}"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/read_components.json"
      }
    },
    {
      "type": "loop",
      "config": {
        "items": "components",
        "item_key": "component",
        "max_concurrency": 0,
        "delay": 0.1,
        "result_key": "built_components",
        "substeps": [
          {
            "type": "conditional",
            "config": {
              "condition": "{% if component_id == component.id or component_id == 'all' %}true{% else %}false{% endif %}",
              "if_true": {
                "steps": [
                  {
                    "type": "execute_recipe",
                    "config": {
                      "recipe_path": "{{ recipe_root | default: 'recipes/recipe_executor' }}/recipes/process_component.json"
                    }
                  }
                ]
              }
            }
          }
        ]
      }
    }
  ]
}


=== File: recipes/codebase_generator/docs/codebase-generator-flow.excalidraw ===
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "main-flow-group",
      "type": "rectangle",
      "x": 120,
      "y": 80,
      "width": 200,
      "height": 600,
      "angle": 0,
      "strokeColor": "transparent",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1012473515,
      "version": 67,
      "versionNonce": 241155753,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745692830338,
      "link": null,
      "locked": false,
      "index": "a0"
    },
    {
      "id": "process-component-group",
      "type": "rectangle",
      "x": 400.01268594946185,
      "y": 46.20345012424031,
      "width": 520,
      "height": 712.9076455248853,
      "angle": 0.001839002649331789,
      "strokeColor": "#999999",
      "backgroundColor": "#f5f5f5",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 40,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1308022037,
      "version": 137,
      "versionNonce": 110702471,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "process-component-label",
          "type": "text"
        },
        {
          "id": "No3GKwzTAcDax9MiojCy8",
          "type": "arrow"
        }
      ],
      "updated": 1745693717684,
      "link": null,
      "locked": false,
      "index": "a1"
    },
    {
      "id": "process-component-label",
      "type": "text",
      "x": 567.9727765866689,
      "y": 51.20345012424031,
      "width": 184.07981872558594,
      "height": 25,
      "angle": 0.001839002649331789,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1949657323,
      "version": 93,
      "versionNonce": 1684897191,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693052141,
      "link": null,
      "locked": false,
      "text": "Process Component",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "baseline": 18,
      "containerId": "process-component-group",
      "originalText": "Process Component",
      "lineHeight": 1.25,
      "index": "a2",
      "autoResize": true
    },
    {
      "id": "start-build",
      "type": "rectangle",
      "x": 93.3333740234375,
      "y": 52.44439697265625,
      "width": 239.111083984375,
      "height": 60,
      "angle": 0,
      "strokeColor": "#1971c2",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1483783083,
      "version": 291,
      "versionNonce": 1102013129,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "start-build-text"
        },
        {
          "id": "TlqYH6PsCDPG6udk91uqK",
          "type": "arrow"
        }
      ],
      "updated": 1745693615405,
      "link": null,
      "locked": false,
      "index": "a5"
    },
    {
      "id": "start-build-text",
      "type": "text",
      "x": 136.6089859008789,
      "y": 69.94439697265625,
      "width": 152.5598602294922,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 575559813,
      "version": 240,
      "versionNonce": 327261385,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693494484,
      "link": null,
      "locked": false,
      "text": "Start build.json",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "start-build",
      "originalText": "Start build.json",
      "lineHeight": 1.25,
      "index": "a6",
      "autoResize": true
    },
    {
      "id": "read-components",
      "type": "rectangle",
      "x": 93.3333740234375,
      "y": 152.44439697265625,
      "width": 239.111083984375,
      "height": 60,
      "angle": 0,
      "strokeColor": "#1971c2",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1284169547,
      "version": 287,
      "versionNonce": 1971950087,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "read-components-text"
        },
        {
          "id": "TlqYH6PsCDPG6udk91uqK",
          "type": "arrow"
        },
        {
          "id": "4kX9qa1KQzQdyPHPMVMQc",
          "type": "arrow"
        }
      ],
      "updated": 1745693667529,
      "link": null,
      "locked": false,
      "index": "a7"
    },
    {
      "id": "read-components-text",
      "type": "text",
      "x": 108.36900329589844,
      "y": 169.94439697265625,
      "width": 209.03982543945312,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1071351147,
      "version": 277,
      "versionNonce": 1483670889,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693494484,
      "link": null,
      "locked": false,
      "text": "Read components.json",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "read-components",
      "originalText": "Read components.json",
      "lineHeight": 1.25,
      "index": "a8",
      "autoResize": true
    },
    {
      "id": "component-loop",
      "type": "rectangle",
      "x": 93.3333740234375,
      "y": 252.44439697265625,
      "width": 239.111083984375,
      "height": 60,
      "angle": 0,
      "strokeColor": "#1971c2",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 889566749,
      "version": 354,
      "versionNonce": 1452406473,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "component-loop-text"
        },
        {
          "id": "WM7UQjc4eu62cZzmhf5n0",
          "type": "arrow"
        },
        {
          "id": "vXkaDZ84Vx95q_If5vxaP",
          "type": "arrow"
        },
        {
          "id": "4kX9qa1KQzQdyPHPMVMQc",
          "type": "arrow"
        },
        {
          "id": "_Ug_hzIUd5ivlzrUxoOpa",
          "type": "arrow"
        }
      ],
      "updated": 1745693760466,
      "link": null,
      "locked": false,
      "index": "a9"
    },
    {
      "id": "component-loop-text",
      "type": "text",
      "x": 136.64898681640625,
      "y": 269.94439697265625,
      "width": 152.4798583984375,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1949657323,
      "version": 308,
      "versionNonce": 1277567047,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693679186,
      "link": null,
      "locked": false,
      "text": "Component Loop",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "component-loop",
      "originalText": "Component Loop",
      "lineHeight": 1.25,
      "index": "aA",
      "autoResize": true
    },
    {
      "id": "match-component",
      "type": "diamond",
      "x": 93.3333740234375,
      "y": 352.44439697265625,
      "width": 239.111083984375,
      "height": 140,
      "angle": 0,
      "strokeColor": "#e6961e",
      "backgroundColor": "#fff9db",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 2
      },
      "seed": 1355480981,
      "version": 482,
      "versionNonce": 2113310055,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "match-component-text"
        },
        {
          "id": "match-to-complete",
          "type": "arrow"
        },
        {
          "id": "ySSobv5QuYECoDtsy9PpX",
          "type": "arrow"
        },
        {
          "id": "WM7UQjc4eu62cZzmhf5n0",
          "type": "arrow"
        },
        {
          "id": "vXkaDZ84Vx95q_If5vxaP",
          "type": "arrow"
        }
      ],
      "updated": 1745693627051,
      "link": null,
      "locked": false,
      "index": "aB"
    },
    {
      "id": "match-component-text",
      "type": "text",
      "x": 158.21517944335938,
      "y": 402.44439697265625,
      "width": 109.79193115234375,
      "height": 40,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1733104981,
      "version": 421,
      "versionNonce": 674825769,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693494484,
      "link": null,
      "locked": false,
      "text": "Match\ncomponent_id?",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "match-component",
      "originalText": "Match component_id?",
      "lineHeight": 1.25,
      "index": "aC",
      "autoResize": true
    },
    {
      "id": "build-complete",
      "type": "rectangle",
      "x": 93.3333740234375,
      "y": 552.4443969726562,
      "width": 239.111083984375,
      "height": 60,
      "angle": 0,
      "strokeColor": "#1971c2",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1483783083,
      "version": 379,
      "versionNonce": 883100809,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "build-complete-text"
        },
        {
          "id": "match-to-complete",
          "type": "arrow"
        }
      ],
      "updated": 1745693494484,
      "link": null,
      "locked": false,
      "index": "aD"
    },
    {
      "id": "build-complete-text",
      "type": "text",
      "x": 143.38898468017578,
      "y": 569.9443969726562,
      "width": 138.99986267089844,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 575559813,
      "version": 336,
      "versionNonce": 394433385,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693494484,
      "link": null,
      "locked": false,
      "text": "Build complete",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "build-complete",
      "originalText": "Build complete",
      "lineHeight": 1.25,
      "index": "aE",
      "autoResize": true
    },
    {
      "id": "start-processing",
      "type": "rectangle",
      "x": 528.2349149533682,
      "y": 99.99999999999999,
      "width": 263.5555419921875,
      "height": 60,
      "angle": 0,
      "strokeColor": "#e03131",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1284169547,
      "version": 394,
      "versionNonce": 2020006951,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "start-processing-text"
        },
        {
          "id": "JrrnHW0v8d0iK7XEIn7KE",
          "type": "arrow"
        },
        {
          "id": "ySSobv5QuYECoDtsy9PpX",
          "type": "arrow"
        }
      ],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "index": "aF"
    },
    {
      "id": "start-processing-text",
      "type": "text",
      "x": 578.6727659055166,
      "y": 117.49999999999999,
      "width": 162.67984008789062,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1071351147,
      "version": 362,
      "versionNonce": 656479495,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "text": "Start processing",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "start-processing",
      "originalText": "Start processing",
      "lineHeight": 1.25,
      "index": "aG",
      "autoResize": true
    },
    {
      "id": "edit-mode",
      "type": "diamond",
      "x": 528.2349149533682,
      "y": 206.88888549804688,
      "width": 263.5555419921875,
      "height": 70,
      "angle": 0,
      "strokeColor": "#e6961e",
      "backgroundColor": "#fff9db",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 2
      },
      "seed": 889566749,
      "version": 556,
      "versionNonce": 1427116199,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "edit-mode-text"
        },
        {
          "id": "Lm5YCicKEwjG6SrJlxhgr",
          "type": "arrow"
        },
        {
          "id": "TKV39LSOmiDZlottftzrO",
          "type": "arrow"
        },
        {
          "id": "JrrnHW0v8d0iK7XEIn7KE",
          "type": "arrow"
        }
      ],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "index": "aH"
    },
    {
      "id": "edit-mode-text",
      "type": "text",
      "x": 607.1638471433096,
      "y": 229.38888549804688,
      "width": 105.91990661621094,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1949657323,
      "version": 447,
      "versionNonce": 1777785223,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "text": "Edit mode?",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "edit-mode",
      "originalText": "Edit mode?",
      "lineHeight": 1.25,
      "index": "aI",
      "autoResize": true
    },
    {
      "id": "generate-code",
      "type": "rectangle",
      "x": 528.2349149533682,
      "y": 793.7777404785157,
      "width": 263.5555419921875,
      "height": 60,
      "angle": 0,
      "strokeColor": "#e03131",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 889566749,
      "version": 959,
      "versionNonce": 1677812201,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "generate-code-text"
        },
        {
          "id": "No3GKwzTAcDax9MiojCy8",
          "type": "arrow"
        },
        {
          "id": "gEZESsXP0bh46KowvfnaH",
          "type": "arrow"
        }
      ],
      "updated": 1745693942088,
      "link": null,
      "locked": false,
      "index": "aX"
    },
    {
      "id": "generate-code-text",
      "type": "text",
      "x": 539.1927701779775,
      "y": 811.2777404785157,
      "width": 241.63983154296875,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1949657323,
      "version": 951,
      "versionNonce": 1731149001,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693942088,
      "link": null,
      "locked": false,
      "text": "Generate code with LLM",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "generate-code",
      "originalText": "Generate code with LLM",
      "lineHeight": 1.25,
      "index": "aY",
      "autoResize": true
    },
    {
      "id": "write-files",
      "type": "rectangle",
      "x": 528.2349149533682,
      "y": 894.3736477578617,
      "width": 263.5555419921875,
      "height": 60,
      "angle": 0,
      "strokeColor": "#e03131",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1355480981,
      "version": 989,
      "versionNonce": 729851241,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "write-files-text"
        },
        {
          "id": "gEZESsXP0bh46KowvfnaH",
          "type": "arrow"
        },
        {
          "id": "pMzLB4zInNiFofgl3Y5rB",
          "type": "arrow"
        }
      ],
      "updated": 1745693942088,
      "link": null,
      "locked": false,
      "index": "aZ"
    },
    {
      "id": "write-files-text",
      "type": "text",
      "x": 569.9927732297353,
      "y": 911.8736477578617,
      "width": 180.03982543945312,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1733104981,
      "version": 968,
      "versionNonce": 351932489,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693942088,
      "link": null,
      "locked": false,
      "text": "Write files to disk",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "write-files",
      "originalText": "Write files to disk",
      "lineHeight": 1.25,
      "index": "aa",
      "autoResize": true
    },
    {
      "id": "component-processed",
      "type": "rectangle",
      "x": 528.2349149533682,
      "y": 993.777801513672,
      "width": 263.5555419921875,
      "height": 60,
      "angle": 0,
      "strokeColor": "#e03131",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1483783083,
      "version": 1065,
      "versionNonce": 1568811241,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "component-processed-text"
        },
        {
          "id": "pMzLB4zInNiFofgl3Y5rB",
          "type": "arrow"
        },
        {
          "id": "_Ug_hzIUd5ivlzrUxoOpa",
          "type": "arrow"
        }
      ],
      "updated": 1745693942088,
      "link": null,
      "locked": false,
      "index": "ab"
    },
    {
      "id": "component-processed-text",
      "type": "text",
      "x": 558.4927884885244,
      "y": 1011.2778015136719,
      "width": 203.039794921875,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 575559813,
      "version": 1043,
      "versionNonce": 587146185,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693942088,
      "link": null,
      "locked": false,
      "text": "Component processed",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "component-processed",
      "originalText": "Component processed",
      "lineHeight": 1.25,
      "index": "ac",
      "autoResize": true
    },
    {
      "id": "match-to-complete",
      "type": "arrow",
      "x": 212.94497197207912,
      "y": 489.0027799411689,
      "width": 0.053221249073601484,
      "height": 63.19257596539569,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 2
      },
      "seed": 575559813,
      "version": 1466,
      "versionNonce": 1428697959,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "match-to-complete-label"
        }
      ],
      "updated": 1745693495409,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          0.053221249073601484,
          63.19257596539569
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "match-component",
        "focus": -1.9525714378687554e-12,
        "gap": 1
      },
      "endBinding": {
        "elementId": "build-complete",
        "focus": 0.001126879562748117,
        "gap": 1
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "index": "ag"
    },
    {
      "id": "match-to-complete-label",
      "type": "text",
      "x": 198.90886039679975,
      "y": 535.6530534632341,
      "width": 76.37994384765625,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1071351147,
      "version": 96,
      "versionNonce": 1715050119,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745692890508,
      "link": null,
      "locked": false,
      "text": "All done",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "match-to-complete",
      "originalText": "All done",
      "lineHeight": 1.25,
      "index": "ah",
      "autoResize": true
    },
    {
      "id": "resource-gathering-group",
      "type": "rectangle",
      "x": 420.0126859494619,
      "y": 327.111083984375,
      "width": 480,
      "height": 414.6666870117187,
      "angle": 0,
      "strokeColor": "#999999",
      "backgroundColor": "#f5f5f5",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 40,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1355480981,
      "version": 180,
      "versionNonce": 1816858887,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "resource-gathering-label",
          "type": "text"
        },
        {
          "id": "No3GKwzTAcDax9MiojCy8",
          "type": "arrow"
        }
      ],
      "updated": 1745693908200,
      "link": null,
      "locked": false,
      "index": "b054"
    },
    {
      "id": "resource-gathering-label",
      "type": "text",
      "x": 568.1009944575176,
      "y": 332.111083984375,
      "width": 190.9598388671875,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1733104981,
      "version": 118,
      "versionNonce": 1473980263,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "text": "Resource Gathering",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "baseline": 18,
      "containerId": "resource-gathering-group",
      "originalText": "Resource Gathering",
      "lineHeight": 1.25,
      "index": "b058",
      "autoResize": true
    },
    {
      "id": "read-existing",
      "type": "rectangle",
      "x": 436.4571439572744,
      "y": 382.8888854980469,
      "width": 200.44445800781256,
      "height": 50,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1355480981,
      "version": 544,
      "versionNonce": 67615143,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "read-existing-text"
        },
        {
          "id": "6N-w-y-fbb-EvC6JZKd_z",
          "type": "arrow"
        },
        {
          "id": "Lm5YCicKEwjG6SrJlxhgr",
          "type": "arrow"
        }
      ],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "index": "b05G"
    },
    {
      "id": "read-existing-text",
      "type": "text",
      "x": 447.68767963818163,
      "y": 395.3888854980469,
      "width": 185.11984252929688,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1733104981,
      "version": 492,
      "versionNonce": 793945863,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "text": "Read existing code",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "read-existing",
      "originalText": "Read existing code",
      "lineHeight": 1.25,
      "index": "b05K",
      "autoResize": true
    },
    {
      "id": "begin-resource",
      "type": "rectangle",
      "x": 690.2348539182119,
      "y": 377.1111145019531,
      "width": 169.77783203124997,
      "height": 60,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1483783083,
      "version": 1134,
      "versionNonce": 974901575,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "begin-resource-text"
        },
        {
          "id": "6N-w-y-fbb-EvC6JZKd_z",
          "type": "arrow"
        },
        {
          "id": "txAQy8HQxjXGPX1j3tK72",
          "type": "arrow"
        },
        {
          "id": "TKV39LSOmiDZlottftzrO",
          "type": "arrow"
        }
      ],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "index": "b05O"
    },
    {
      "id": "begin-resource-text",
      "type": "text",
      "x": 707.8720668452129,
      "y": 382.1111145019531,
      "width": 141.63986206054688,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 575559813,
      "version": 1046,
      "versionNonce": 9532871,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Begin resource\ngathering",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 43,
      "containerId": "begin-resource",
      "originalText": "Begin resource gathering",
      "lineHeight": 1.25,
      "index": "b05V",
      "autoResize": true
    },
    {
      "id": "read-resources",
      "type": "rectangle",
      "x": 560.6793119260244,
      "y": 485.1111145019531,
      "width": 200,
      "height": 50,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1284169547,
      "version": 577,
      "versionNonce": 2072375303,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "read-resources-text"
        },
        {
          "id": "6VmKlz1y04BVdreg61LvH",
          "type": "arrow"
        },
        {
          "id": "Vgds8WcHv-rwllevydla4",
          "type": "arrow"
        },
        {
          "id": "Z-3bD58eObNSkj3oJF7A7",
          "type": "arrow"
        },
        {
          "id": "InCdCyFcpdufmS8GII_rx",
          "type": "arrow"
        },
        {
          "id": "txAQy8HQxjXGPX1j3tK72",
          "type": "arrow"
        }
      ],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "index": "b05Z"
    },
    {
      "id": "read-resources-text",
      "type": "text",
      "x": 574.2475398676738,
      "y": 485.1111145019531,
      "width": 180,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1071351147,
      "version": 557,
      "versionNonce": 1509555911,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Read component \nresources",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 43,
      "containerId": "read-resources",
      "originalText": "Read component resources",
      "lineHeight": 1.25,
      "index": "b05d",
      "autoResize": true
    },
    {
      "id": "component-spec",
      "type": "rectangle",
      "x": 445.79045694555566,
      "y": 576.2221984863281,
      "width": 160,
      "height": 50,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 889566749,
      "version": 613,
      "versionNonce": 1495283975,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "component-spec-text"
        },
        {
          "id": "6VmKlz1y04BVdreg61LvH",
          "type": "arrow"
        }
      ],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "index": "b05l"
    },
    {
      "id": "component-spec-text",
      "type": "text",
      "x": 460.3586848872051,
      "y": 576.2221984863281,
      "width": 138,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1949657323,
      "version": 597,
      "versionNonce": 925688647,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Component \nspec & docs",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 43,
      "containerId": "component-spec",
      "originalText": "Component spec & docs",
      "lineHeight": 1.25,
      "index": "b05p",
      "autoResize": true
    },
    {
      "id": "dependency-specs",
      "type": "rectangle",
      "x": 710.0126859494619,
      "y": 574.8888854980469,
      "width": 160,
      "height": 50,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1355480981,
      "version": 708,
      "versionNonce": 1631845767,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "dependency-specs-text"
        },
        {
          "id": "Z-3bD58eObNSkj3oJF7A7",
          "type": "arrow"
        }
      ],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "index": "b05t"
    },
    {
      "id": "dependency-specs-text",
      "type": "text",
      "x": 718.5809138911113,
      "y": 574.8888854980469,
      "width": 150,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1733104981,
      "version": 700,
      "versionNonce": 1267304391,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Dependency \nspecs",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 43,
      "containerId": "dependency-specs",
      "originalText": "Dependency specs",
      "lineHeight": 1.25,
      "index": "b06",
      "autoResize": true
    },
    {
      "id": "reference-docs",
      "type": "rectangle",
      "x": 445.79045694555566,
      "y": 674.6666564941406,
      "width": 160,
      "height": 50,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1483783083,
      "version": 694,
      "versionNonce": 824279559,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "reference-docs-text"
        },
        {
          "id": "Vgds8WcHv-rwllevydla4",
          "type": "arrow"
        }
      ],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "index": "b068"
    },
    {
      "id": "reference-docs-text",
      "type": "text",
      "x": 460.3586848872051,
      "y": 674.6666564941406,
      "width": 138,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 575559813,
      "version": 713,
      "versionNonce": 1412426823,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Reference \ndocumentation",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 43,
      "containerId": "reference-docs",
      "originalText": "Reference documentation",
      "lineHeight": 1.25,
      "index": "b06G",
      "autoResize": true
    },
    {
      "id": "implementation-guidance",
      "type": "rectangle",
      "x": 710.0126859494619,
      "y": 674.2221984863281,
      "width": 160,
      "height": 50,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1284169547,
      "version": 757,
      "versionNonce": 1037616775,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "implementation-guidance-text"
        },
        {
          "id": "impl-to-generate",
          "type": "arrow"
        },
        {
          "id": "InCdCyFcpdufmS8GII_rx",
          "type": "arrow"
        }
      ],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "index": "b06V"
    },
    {
      "id": "implementation-guidance-text",
      "type": "text",
      "x": 718.5809138911113,
      "y": 674.2221984863281,
      "width": 150,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1071351147,
      "version": 787,
      "versionNonce": 2118127815,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Implementation \nguidance",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 43,
      "containerId": "implementation-guidance",
      "originalText": "Implementation guidance",
      "lineHeight": 1.25,
      "index": "b06d",
      "autoResize": true
    },
    {
      "id": "6VmKlz1y04BVdreg61LvH",
      "type": "arrow",
      "x": 545.7727229981788,
      "y": 572.8052642622937,
      "width": 47.30404982368725,
      "height": 36.60343761385059,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "index": "b06l",
      "roundness": {
        "type": 2
      },
      "seed": 1801237897,
      "version": 87,
      "versionNonce": 703447047,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694355350,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          47.30404982368725,
          -36.60343761385059
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "component-spec",
        "focus": -0.14907197530670954,
        "gap": 9.499993006387399
      },
      "endBinding": {
        "elementId": "read-resources",
        "focus": 0.24612620907912405,
        "gap": 4.055548985800101
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "Vgds8WcHv-rwllevydla4",
      "type": "arrow",
      "x": 599.8037261443935,
      "y": 671.6074528069355,
      "width": 40.53882491883894,
      "height": 133.0416386396846,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "index": "b07",
      "roundness": {
        "type": 2
      },
      "seed": 1818662599,
      "version": 96,
      "versionNonce": 80963561,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694355350,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          40.53882491883894,
          -133.0416386396846
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "reference-docs",
        "focus": 0.7471482901769576,
        "gap": 8.624072449867985
      },
      "endBinding": {
        "elementId": "read-resources",
        "focus": 0.10754451607894333,
        "gap": 11.166663487753226
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "Z-3bD58eObNSkj3oJF7A7",
      "type": "arrow",
      "x": 757.3322058954111,
      "y": 571.2875954741792,
      "width": 33.84082560758338,
      "height": 33.515771920341535,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "index": "b078",
      "roundness": {
        "type": 2
      },
      "seed": 1545336231,
      "version": 87,
      "versionNonce": 1919297319,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694355350,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -33.84082560758338,
          -33.515771920341535
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "dependency-specs",
        "focus": -0.03612419808308407,
        "gap": 9.944451014199899
      },
      "endBinding": {
        "elementId": "read-resources",
        "focus": -0.2695214623176754,
        "gap": 8.944434483846976
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "InCdCyFcpdufmS8GII_rx",
      "type": "arrow",
      "x": 716.1137583068642,
      "y": 670.0320131514782,
      "width": 44.14977939494236,
      "height": 130.62735573922714,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "index": "b07G",
      "roundness": {
        "type": 2
      },
      "seed": 553239817,
      "version": 98,
      "versionNonce": 1808827081,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694355350,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -44.14977939494236,
          -130.62735573922714
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "implementation-guidance",
        "focus": -0.7239509963766171,
        "gap": 11.335609221312886
      },
      "endBinding": {
        "elementId": "read-resources",
        "focus": -0.01184352091943551,
        "gap": 13.388892491659476
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "6N-w-y-fbb-EvC6JZKd_z",
      "type": "arrow",
      "x": 641.0207490585129,
      "y": 405.1329125346552,
      "width": 44.09482620891515,
      "height": 0.5098887052896544,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "index": "b07V",
      "roundness": {
        "type": 2
      },
      "seed": 43314087,
      "version": 137,
      "versionNonce": 1501866567,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745694355350,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          44.09482620891515,
          0.5098887052896544
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "read-existing",
        "focus": -0.1640780531010233,
        "gap": 4.2777599758601355
      },
      "endBinding": {
        "elementId": "begin-resource",
        "focus": 0.02852590417115995,
        "gap": 5.4999499850773645
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "txAQy8HQxjXGPX1j3tK72",
      "type": "arrow",
      "x": 735.3897552089527,
      "y": 443.1117345279079,
      "width": 27.741264404019148,
      "height": 36.04802330088597,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "index": "b07l",
      "roundness": {
        "type": 2
      },
      "seed": 180458663,
      "version": 194,
      "versionNonce": 1848066473,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694355350,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -27.741264404019148,
          36.04802330088597
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "begin-resource",
        "focus": 0.11140668419726422,
        "gap": 6.000620025954788
      },
      "endBinding": {
        "elementId": "read-resources",
        "focus": 0.19414877883603365,
        "gap": 5.951356673159239
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "Lm5YCicKEwjG6SrJlxhgr",
      "type": "arrow",
      "x": 555.6585971353172,
      "y": 261.8426683137163,
      "width": 84.72089247115377,
      "height": 110.5915995218673,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b08",
      "roundness": {
        "type": 2
      },
      "seed": 936758247,
      "version": 277,
      "versionNonce": 73504839,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "xVAgpR0GaV1f3TmIDtleh"
        }
      ],
      "updated": 1745694322821,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -55.38083715945703,
          33.3795365834244
        ],
        [
          -84.72089247115377,
          110.5915995218673
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "edit-mode",
        "focus": 0.32587639018981124,
        "gap": 11.070642880362529
      },
      "endBinding": {
        "elementId": "read-existing",
        "focus": -0.7219531043557784,
        "gap": 10.454617662463306
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "xVAgpR0GaV1f3TmIDtleh",
      "type": "text",
      "x": 659.5709798633462,
      "y": 303.55554135640557,
      "width": 31.679977416992188,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b09",
      "roundness": null,
      "seed": 158002921,
      "version": 6,
      "versionNonce": 1413940903,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Yes",
      "fontSize": 20,
      "fontFamily": 5,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "Lm5YCicKEwjG6SrJlxhgr",
      "originalText": "Yes",
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "id": "TKV39LSOmiDZlottftzrO",
      "type": "arrow",
      "x": 757.0488218945784,
      "y": 261.9059533511263,
      "width": 75.31010413314891,
      "height": 108.57343605155523,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0A",
      "roundness": {
        "type": 2
      },
      "seed": 687006793,
      "version": 165,
      "versionNonce": 509096873,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "8RJwXFA9LGNWiMUP2N8CI"
        }
      ],
      "updated": 1745694322821,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          49.89556405784424,
          42.205137044061246
        ],
        [
          75.31010413314891,
          108.57343605155523
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "edit-mode",
        "focus": -0.4709659440177606,
        "gap": 9.318459145273223
      },
      "endBinding": {
        "elementId": "begin-resource",
        "focus": 0.7394161091333835,
        "gap": 6.631725099271591
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "8RJwXFA9LGNWiMUP2N8CI",
      "type": "text",
      "x": 629.5302613520402,
      "y": 299.11110623677666,
      "width": 24.639999389648438,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0B",
      "roundness": null,
      "seed": 1060006023,
      "version": 5,
      "versionNonce": 1811204327,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "No",
      "fontSize": 20,
      "fontFamily": 5,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "TKV39LSOmiDZlottftzrO",
      "originalText": "No",
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "id": "JrrnHW0v8d0iK7XEIn7KE",
      "type": "arrow",
      "x": 657.9672537188909,
      "y": 162.24967745501525,
      "width": 3.5916628735916447,
      "height": 41.40642020378138,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0C",
      "roundness": {
        "type": 2
      },
      "seed": 411630215,
      "version": 83,
      "versionNonce": 959772519,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694322821,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          3.5916628735916447,
          41.40642020378138
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "start-processing",
        "focus": 0.023683167370835805,
        "gap": 8.499991310968312
      },
      "endBinding": {
        "elementId": "edit-mode",
        "focus": 0.011216488877313238,
        "gap": 5.531463613547234
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "ySSobv5QuYECoDtsy9PpX",
      "type": "arrow",
      "x": 322.4084843739512,
      "y": 408.2221984863281,
      "width": 192.80568654826016,
      "height": 278.9443692101363,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0D",
      "roundness": {
        "type": 2
      },
      "seed": 180146279,
      "version": 566,
      "versionNonce": 1780497511,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "NKUopUtAQg7Fs4YyyBWRr"
        }
      ],
      "updated": 1745694288798,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          40.09150460581526,
          -54.55557017855995
        ],
        [
          76.53590157847151,
          -278.9443692101363
        ],
        [
          192.80568654826016,
          -278.7729242076256
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "match-component",
        "focus": 1.127588354989266,
        "gap": 8.318410397820681
      },
      "endBinding": {
        "elementId": "start-processing",
        "focus": 0.01116812420855947,
        "gap": 13.020744031156823
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "NKUopUtAQg7Fs4YyyBWRr",
      "type": "text",
      "x": 359.5488552517391,
      "y": 330.50006887647936,
      "width": 31.679977416992188,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0E",
      "roundness": null,
      "seed": 1049245513,
      "version": 6,
      "versionNonce": 2050530567,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745693525142,
      "link": null,
      "locked": false,
      "text": "Yes",
      "fontSize": 20,
      "fontFamily": 5,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "ySSobv5QuYECoDtsy9PpX",
      "originalText": "Yes",
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "id": "WM7UQjc4eu62cZzmhf5n0",
      "type": "arrow",
      "x": 110.82625442060541,
      "y": 399.3332824707031,
      "width": 21.659578429120216,
      "height": 80.21141096777939,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "dashed",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0H",
      "roundness": {
        "type": 2
      },
      "seed": 1800707817,
      "version": 255,
      "versionNonce": 1901156903,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "6ySc2-R0LtKidxe2b4DF8"
        }
      ],
      "updated": 1745694278439,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -21.659578429120216,
          -31.055503633286264
        ],
        [
          -14.32185769629072,
          -80.21141096777939
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "match-component",
        "focus": -1.0307036212977265,
        "gap": 11.857736154251425
      },
      "endBinding": {
        "elementId": "component-loop",
        "focus": 0.8941879693598793,
        "gap": 9.03502031610239
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "6ySc2-R0LtKidxe2b4DF8",
      "type": "text",
      "x": 60.2066921658016,
      "y": 347.77777883741686,
      "width": 97.91996765136719,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0I",
      "roundness": null,
      "seed": 799412681,
      "version": 11,
      "versionNonce": 669770089,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745693587258,
      "link": null,
      "locked": false,
      "text": "No / Next",
      "fontSize": 20,
      "fontFamily": 5,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "WM7UQjc4eu62cZzmhf5n0",
      "originalText": "No / Next",
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "id": "TlqYH6PsCDPG6udk91uqK",
      "type": "arrow",
      "x": 221.6332405573659,
      "y": 117.99998792012626,
      "width": 0,
      "height": 24.000000000000014,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0J",
      "roundness": {
        "type": 2
      },
      "seed": 267050183,
      "version": 39,
      "versionNonce": 1514526345,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694322821,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          0,
          24.000000000000014
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "start-build",
        "focus": -0.07314026933450148,
        "gap": 5.555590947470009
      },
      "endBinding": {
        "elementId": "read-components",
        "focus": 0.07314026933450145,
        "gap": 10.444409052529977
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "vXkaDZ84Vx95q_If5vxaP",
      "type": "arrow",
      "x": 216.454383877382,
      "y": 315.0942248689289,
      "width": 0.939056935310191,
      "height": 32.087568165422226,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0L",
      "roundness": {
        "type": 2
      },
      "seed": 538640583,
      "version": 47,
      "versionNonce": 915370631,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694322821,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -0.939056935310191,
          32.087568165422226
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "component-loop",
        "focus": -0.037539217727723284,
        "gap": 2.6498278962726545
      },
      "endBinding": {
        "elementId": "match-component",
        "focus": 0.00605453416230627,
        "gap": 9.782672166268867
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "4kX9qa1KQzQdyPHPMVMQc",
      "type": "arrow",
      "x": 218.34720075878334,
      "y": 214.5142930292676,
      "width": 0.02258885210054018,
      "height": 36.13951050089938,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0M",
      "roundness": {
        "type": 2
      },
      "seed": 1702849671,
      "version": 424,
      "versionNonce": 1379671401,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694322821,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -0.02258885210054018,
          36.13951050089938
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "read-components",
        "focus": -0.0458152814053177,
        "gap": 2.0698960566113556
      },
      "endBinding": {
        "elementId": "component-loop",
        "focus": 0.04529255544040108,
        "gap": 1.7905934424892678
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "No3GKwzTAcDax9MiojCy8",
      "type": "arrow",
      "x": 665.0829553727528,
      "y": 743.9962399756761,
      "width": 1.2286518662745038,
      "height": 49.204726843819344,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0N",
      "roundness": {
        "type": 2
      },
      "seed": 996460329,
      "version": 203,
      "versionNonce": 2115357193,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694335782,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          1.2286518662745038,
          49.204726843819344
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "resource-gathering-group",
        "focus": 0.00034113018436506915,
        "gap": 3.389306545125919
      },
      "endBinding": {
        "elementId": "generate-code",
        "focus": 0.05482991593078177,
        "gap": 2.454290873120044
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "gEZESsXP0bh46KowvfnaH",
      "type": "arrow",
      "x": 660.0126455360576,
      "y": 854.3383522863093,
      "width": 0.24589269522857649,
      "height": 38.87115588992208,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0O",
      "roundness": {
        "type": 2
      },
      "seed": 1419197705,
      "version": 261,
      "versionNonce": 1854568199,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694335782,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -0.24589269522857649,
          38.87115588992208
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "generate-code",
        "focus": -0.0014646109516322778,
        "gap": 1
      },
      "endBinding": {
        "elementId": "write-files",
        "focus": -0.0033574349763533357,
        "gap": 1.1641395816303657
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "pMzLB4zInNiFofgl3Y5rB",
      "type": "arrow",
      "x": 660.3273200205763,
      "y": 954.8254451370203,
      "width": 1.6762311007936432,
      "height": 37.16520851425264,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0P",
      "roundness": {
        "type": 2
      },
      "seed": 810555273,
      "version": 280,
      "versionNonce": 1858183401,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694335782,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -1.6762311007936432,
          37.16520851425264
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "write-files",
        "focus": -0.012679826081854605,
        "gap": 1
      },
      "endBinding": {
        "elementId": "component-processed",
        "focus": -0.020996382804093442,
        "gap": 1.7871478623990242
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "_Ug_hzIUd5ivlzrUxoOpa",
      "type": "arrow",
      "x": 517.3991931202238,
      "y": 1029.3560781594817,
      "width": 534.4547156150668,
      "height": 751.5995291234158,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "dashed",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0Q",
      "roundness": {
        "type": 2
      },
      "seed": 576766729,
      "version": 1542,
      "versionNonce": 992018345,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745694215011,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -197.5658911521761,
          -55.800580248238475
        ],
        [
          -421.1214331443636,
          -233.63387161990215
        ],
        [
          -534.4547156150668,
          -536.0783077461871
        ],
        [
          -513.1214331443637,
          -741.6339021374803
        ],
        [
          -434.929376342646,
          -751.5995291234158
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "component-processed",
        "focus": -0.6822153893110063,
        "gap": 10.835721833144362
      },
      "endBinding": {
        "elementId": "component-loop",
        "focus": 0.4710666539072743,
        "gap": 10.863557245859681
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    }
  ],
  "appState": {
    "gridSize": 20,
    "gridStep": 5,
    "gridModeEnabled": false,
    "viewBackgroundColor": "#f5f5f5"
  },
  "files": {}
}

=== File: recipes/codebase_generator/docs/codebase-generator-flow.svg ===
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 962.192248250424 1028.0518890578503" width="962.192248250424" height="1028.0518890578503"><!-- svg-source:excalidraw --><metadata></metadata><defs><style class="style-fonts">
      @font-face { font-family: Virgil; src: url(data:font/woff2;base64,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); }
      @font-face { font-family: Excalifont; src: url(data:font/woff2;base64,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); }</style></defs><rect x="0" y="0" width="962.192248250424" height="1028.0518890578503" fill="#f5f5f5"></rect><g stroke-linecap="round" transform="translate(151.5244827968972 44.27408754417837) rotate(0 100 300)"><path d="M0 0 C52.77 1.58, 103.46 1.48, 200 0 M0 0 C67.68 0.26, 134.44 -0.06, 200 0 M200 0 C198.68 129.2, 198.5 259.78, 200 600 M200 0 C201.81 146.95, 202.52 293.97, 200 600 M200 600 C156.19 600.38, 110.76 600.14, 0 600 M200 600 C132.57 600.69, 64.2 601.29, 0 600 M0 600 C-0.24 380.57, 0.38 160.34, 0 0 M0 600 C-2.33 439.81, -2.54 279.39, 0 0" stroke="transparent" stroke-width="1" fill="none"></path></g><g stroke-opacity="0.4" fill-opacity="0.4" stroke-linecap="round" transform="translate(431.53716874635904 10.477537668418684) rotate(0.10536709032008844 260 356.45382276244266)"><path d="M32 0 C181.79 0.66, 333.44 -1.2, 488 0 C512.45 -0.26, 522.77 9.03, 520 32 C515.86 256.11, 516.56 478.99, 520 680.91 C523.46 704.27, 509.72 714.55, 488 712.91 C346.26 713.31, 203.05 715.18, 32 712.91 C9.44 712.05, -1.63 705.21, 0 680.91 C0.45 537.86, -0.83 396.25, 0 32 C2.9 13, 10.46 0.5, 32 0" stroke="none" stroke-width="0" fill="#f5f5f5"></path><path d="M32 0 C181.7 2.02, 330.36 2.24, 488 0 M32 0 C143.64 -1.04, 256.04 -0.6, 488 0 M488 0 C510.71 -1.07, 520.72 11.94, 520 32 M488 0 C508.92 -1.82, 518.93 11.04, 520 32 M520 32 C521.77 259.66, 522.08 486.17, 520 680.91 M520 32 C519.3 227.24, 519.48 422.1, 520 680.91 M520 680.91 C520.48 703.97, 508.59 711.52, 488 712.91 M520 680.91 C519.23 703.4, 507.49 711.33, 488 712.91 M488 712.91 C382.11 712.72, 276.44 712.01, 32 712.91 M488 712.91 C354.23 714.14, 220.52 714.07, 32 712.91 M32 712.91 C11.35 714.89, -0.84 704.24, 0 680.91 M32 712.91 C10.83 714.71, 2.21 701.5, 0 680.91 M0 680.91 C0.1 463.26, 0.33 246.16, 0 32 M0 680.91 C1.23 520.46, 1.32 360.78, 0 32 M0 32 C-1.26 12.34, 10.09 1.43, 32 0 M0 32 C-0.82 12.04, 9.51 -0.28, 32 0" stroke="#999999" stroke-width="1" fill="none"></path></g><g transform="translate(599.4972593835662 15.477537668418684) rotate(0.10536709032008844 92.03990936279297 12.499999999999996)"><text x="92.03990936279297" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Process Component</text></g><g stroke-linecap="round" transform="translate(124.85785682033469 16.71848451683462) rotate(0 119.5555419921875 30)"><path d="M15 0 C85.51 0.55, 155.71 -0.17, 224.11 0 C232.04 -3.06, 241.2 8.28, 239.11 15 C235.98 21.58, 238.58 28.39, 239.11 45 C236 53.36, 230.8 57.21, 224.11 60 C141.25 62.82, 60.08 63.47, 15 60 C3.43 60.83, 0.44 54.28, 0 45 C-0.49 37.61, 0.67 34.68, 0 15 C-3.5 8.36, 2.14 -2.42, 15 0" stroke="none" stroke-width="0" fill="#a5d8ff"></path><path d="M15 0 C74 2.61, 131.87 2.4, 224.11 0 M15 0 C67.8 -1.62, 119.73 -1.97, 224.11 0 M224.11 0 C235.7 -0.51, 241.05 4.95, 239.11 15 M224.11 0 C233.23 -0.06, 238.81 3.87, 239.11 15 M239.11 15 C240.15 21.29, 240.51 28.47, 239.11 45 M239.11 15 C240.04 24.55, 239.61 33.49, 239.11 45 M239.11 45 C238.85 56.4, 232.54 60.76, 224.11 60 M239.11 45 C240.16 57.23, 232.46 60.95, 224.11 60 M224.11 60 C162.58 59.59, 101.65 57.88, 15 60 M224.11 60 C155.83 61.64, 88.74 61.7, 15 60 M15 60 C5.81 61, -1.07 55.49, 0 45 M15 60 C5.93 57.85, -1 56.13, 0 45 M0 45 C1.64 37.59, -1.79 33.22, 0 15 M0 45 C-1.25 37.63, 0.4 32.29, 0 15 M0 15 C1.31 5.08, 5.58 0.05, 15 0 M0 15 C0.88 6.67, 2.72 -0.72, 15 0" stroke="#1971c2" stroke-width="1" fill="none"></path></g><g transform="translate(168.1334686977761 34.21848451683462) rotate(0 76.2799301147461 12.5)"><text x="76.2799301147461" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Start build.json</text></g><g stroke-linecap="round" transform="translate(124.85785682033469 116.71848451683462) rotate(0 119.5555419921875 30)"><path d="M15 0 C98.73 -2.5, 180.14 2.89, 224.11 0 C233.84 0.82, 237.06 7.26, 239.11 15 C242.99 24.26, 241.66 29.88, 239.11 45 C236.59 55.8, 233.12 62.93, 224.11 60 C152.35 56.37, 80.23 58.67, 15 60 C3.39 56.5, 0.21 51.71, 0 45 C2.87 38.7, -0.94 26.6, 0 15 C2.49 6.26, 7.23 -3.24, 15 0" stroke="none" stroke-width="0" fill="#a5d8ff"></path><path d="M15 0 C78.1 -0.21, 139.7 0.43, 224.11 0 M15 0 C71.5 -1.48, 127.42 -0.58, 224.11 0 M224.11 0 C233.2 -0.42, 241.06 6.04, 239.11 15 M224.11 0 C233.42 -1.31, 237.74 2.86, 239.11 15 M239.11 15 C240.36 26.72, 237.64 36.9, 239.11 45 M239.11 15 C238.38 24.95, 240.11 35.46, 239.11 45 M239.11 45 C238.4 53.59, 232.59 61.31, 224.11 60 M239.11 45 C237.28 56.85, 232.48 58.73, 224.11 60 M224.11 60 C173.09 61.76, 124.09 61.93, 15 60 M224.11 60 C178.17 59.29, 132.56 59.2, 15 60 M15 60 C3.11 58.66, 1.24 55.78, 0 45 M15 60 C5.05 58.91, 0.46 55, 0 45 M0 45 C2.08 33.37, 1.9 25.15, 0 15 M0 45 C0.33 38.92, -0.25 31.65, 0 15 M0 15 C0.49 4.64, 3.36 0.82, 15 0 M0 15 C1.96 6.18, 3.79 0.8, 15 0" stroke="#1971c2" stroke-width="1" fill="none"></path></g><g transform="translate(139.89348609279563 134.21848451683462) rotate(0 104.51991271972656 12.5)"><text x="104.51991271972656" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Read components.json</text></g><g stroke-linecap="round" transform="translate(124.85785682033469 216.71848451683462) rotate(0 119.5555419921875 30)"><path d="M15 0 C65.43 -4.33, 118.95 -0.45, 224.11 0 C233.42 -0.14, 236.65 3.7, 239.11 15 C239.94 20.23, 238.16 26.33, 239.11 45 C239.77 52.12, 234.11 57.89, 224.11 60 C143.76 59.77, 68.12 59.38, 15 60 C1.59 58.64, -1.63 54.26, 0 45 C2.19 39.11, -1.51 28.86, 0 15 C-3.6 3.29, 8.17 3.44, 15 0" stroke="none" stroke-width="0" fill="#a5d8ff"></path><path d="M15 0 C81.37 2.71, 149.53 1.07, 224.11 0 M15 0 C65.84 -2.01, 115.37 -0.42, 224.11 0 M224.11 0 C233.62 0.7, 239.01 6.7, 239.11 15 M224.11 0 C233.32 -1.57, 240.83 2.84, 239.11 15 M239.11 15 C237.67 23.85, 239.88 36.07, 239.11 45 M239.11 15 C239.06 20.88, 239.38 28.62, 239.11 45 M239.11 45 C240.08 55.5, 235.8 59.94, 224.11 60 M239.11 45 C239.56 53.77, 232.58 57.71, 224.11 60 M224.11 60 C146.16 62.85, 70.25 60.26, 15 60 M224.11 60 C151.54 58.67, 79.07 58.77, 15 60 M15 60 C3.83 61.59, 0.65 56.92, 0 45 M15 60 C6.48 57.86, 0.55 56.62, 0 45 M0 45 C0.1 33.91, 0.2 24.97, 0 15 M0 45 C1.02 36.06, -0.07 27.92, 0 15 M0 15 C-0.17 5.42, 4.24 -0.08, 15 0 M0 15 C1.84 7.23, 3.98 -1.21, 15 0" stroke="#1971c2" stroke-width="1" fill="none"></path></g><g transform="translate(168.17346961330344 234.21848451683462) rotate(0 76.23992919921875 12.5)"><text x="76.23992919921875" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Component Loop</text></g><g stroke-linecap="round" transform="translate(124.85785682033469 316.7184845168346) rotate(0 119.5555419921875 70)"><path d="M150 17.75 C164.88 30.89, 180.99 36.16, 209.11 53.25 C238.19 72.99, 241.83 68.75, 209.11 88.75 C185.08 100.66, 161.47 112.81, 150 122.25 C120.84 140.11, 118.4 142.1, 90 122.25 C64.43 105.87, 47.62 99.2, 30 88.75 C-2.92 73.38, -3.06 69.52, 30 53.25 C54.34 38.7, 72.16 29.31, 90 17.75 C122.9 -3.14, 119.93 0.73, 150 17.75" stroke="none" stroke-width="0" fill="#fff9db"></path><path d="M150 17.75 C166.09 28.06, 184.97 38.39, 209.11 53.25 M150 17.75 C169.17 29.31, 187.64 41.42, 209.11 53.25 M209.11 53.25 C239.21 71.06, 239.08 70.01, 209.11 88.75 M209.11 53.25 C240.12 69.56, 240.89 72.24, 209.11 88.75 M209.11 88.75 C190.45 97.38, 169.42 109.92, 150 122.25 M209.11 88.75 C187.62 101.16, 167.39 113.01, 150 122.25 M150 122.25 C119.99 140.38, 119.5 140.98, 90 122.25 M150 122.25 C120.8 140.03, 121.51 140.95, 90 122.25 M90 122.25 C77.36 116.62, 65.24 106.55, 30 88.75 M90 122.25 C74.49 113.47, 56.6 103.33, 30 88.75 M30 88.75 C-0.38 70.12, -0.99 69.61, 30 53.25 M30 88.75 C1.13 71.9, -2.18 70.6, 30 53.25 M30 53.25 C47.61 42.83, 62.07 32.49, 90 17.75 M30 53.25 C43.79 45.51, 57.45 36.98, 90 17.75 M90 17.75 C120.74 0.14, 118.76 -0.46, 150 17.75 M90 17.75 C120.51 -0.57, 118.86 -0.06, 150 17.75" stroke="#e6961e" stroke-width="1" fill="none"></path></g><g transform="translate(189.73966224025656 366.7184845168346) rotate(0 54.895965576171875 20)"><text x="54.895965576171875" y="14.096" font-family="Virgil, Segoe UI Emoji" font-size="16px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Match</text><text x="54.895965576171875" y="34.096000000000004" font-family="Virgil, Segoe UI Emoji" font-size="16px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">component_id?</text></g><g stroke-linecap="round" transform="translate(124.85785682033469 516.7184845168347) rotate(0 119.5555419921875 30)"><path d="M15 0 C85.51 0.55, 155.71 -0.17, 224.11 0 C232.04 -3.06, 241.2 8.28, 239.11 15 C235.98 21.58, 238.58 28.39, 239.11 45 C236 53.36, 230.8 57.21, 224.11 60 C141.25 62.82, 60.08 63.47, 15 60 C3.43 60.83, 0.44 54.28, 0 45 C-0.49 37.61, 0.67 34.68, 0 15 C-3.5 8.36, 2.14 -2.42, 15 0" stroke="none" stroke-width="0" fill="#a5d8ff"></path><path d="M15 0 C74 2.61, 131.87 2.4, 224.11 0 M15 0 C67.8 -1.62, 119.73 -1.97, 224.11 0 M224.11 0 C235.7 -0.51, 241.05 4.95, 239.11 15 M224.11 0 C233.23 -0.06, 238.81 3.87, 239.11 15 M239.11 15 C240.15 21.29, 240.51 28.47, 239.11 45 M239.11 15 C240.04 24.55, 239.61 33.49, 239.11 45 M239.11 45 C238.85 56.4, 232.54 60.76, 224.11 60 M239.11 45 C240.16 57.23, 232.46 60.95, 224.11 60 M224.11 60 C162.58 59.59, 101.65 57.88, 15 60 M224.11 60 C155.83 61.64, 88.74 61.7, 15 60 M15 60 C5.81 61, -1.07 55.49, 0 45 M15 60 C5.93 57.85, -1 56.13, 0 45 M0 45 C1.64 37.59, -1.79 33.22, 0 15 M0 45 C-1.25 37.63, 0.4 32.29, 0 15 M0 15 C1.31 5.08, 5.58 0.05, 15 0 M0 15 C0.88 6.67, 2.72 -0.72, 15 0" stroke="#1971c2" stroke-width="1" fill="none"></path></g><g transform="translate(174.91346747707297 534.2184845168347) rotate(0 69.49993133544922 12.5)"><text x="69.49993133544922" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Build complete</text></g><g stroke-linecap="round" transform="translate(559.7593977502654 64.27408754417836) rotate(0 131.77777099609375 30.000000000000007)"><path d="M15 0 C108.44 -2.34, 199.67 2.8, 248.56 0 C258.28 0.82, 261.51 7.26, 263.56 15 C267.43 24.26, 266.11 29.88, 263.56 45 C261.03 55.8, 257.56 62.93, 248.56 60 C168.45 56.47, 88 58.66, 15 60 C3.39 56.5, 0.21 51.71, 0 45 C2.87 38.7, -0.94 26.6, 0 15 C2.49 6.26, 7.23 -3.24, 15 0" stroke="none" stroke-width="0" fill="#ffc9c9"></path><path d="M15 0 C85.28 -0.32, 154.14 0.3, 248.56 0 M15 0 C78.07 -1.56, 140.6 -0.71, 248.56 0 M248.56 0 C257.65 -0.42, 265.5 6.04, 263.56 15 M248.56 0 C257.87 -1.31, 262.18 2.86, 263.56 15 M263.56 15 C264.81 26.72, 262.08 36.9, 263.56 45 M263.56 15 C262.83 24.95, 264.56 35.46, 263.56 45 M263.56 45 C262.84 53.59, 257.04 61.31, 248.56 60 M263.56 45 C261.72 56.85, 256.92 58.73, 248.56 60 M248.56 60 C191.61 61.79, 136.59 61.96, 15 60 M248.56 60 C197.27 59.16, 146.3 59.07, 15 60 M15 60 C3.11 58.66, 1.24 55.78, 0 45 M15 60 C5.05 58.91, 0.46 55, 0 45 M0 45 C2.08 33.37, 1.9 25.15, 0 15 M0 45 C0.33 38.92, -0.25 31.65, 0 15 M0 15 C0.49 4.64, 3.36 0.82, 15 0 M0 15 C1.96 6.18, 3.79 0.8, 15 0" stroke="#e03131" stroke-width="1" fill="none"></path></g><g transform="translate(610.1972487024138 81.77408754417836) rotate(0 81.33992004394531 12.500000000000007)"><text x="81.33992004394531" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Start processing</text></g><g stroke-linecap="round" transform="translate(559.7593977502654 171.16297304222525) rotate(0 131.77777099609375 35)"><path d="M165 9 C178.55 9.69, 195.51 18.67, 230.56 27 C262.86 35.86, 261.09 34.7, 230.56 45 C217.95 48.04, 202.69 51.26, 165 61 C132.66 67.12, 132 67.89, 99 61 C71.81 53.89, 50.02 47.46, 33 45 C-3.41 34.64, -1.63 35.26, 33 27 C49.49 24.09, 60.06 16.44, 99 9 C128.4 -1.71, 135.17 3.44, 165 9" stroke="none" stroke-width="0" fill="#fff9db"></path><path d="M165 9 C184.66 17.09, 206.22 21.08, 230.56 27 M165 9 C181.3 12.04, 196.28 18.16, 230.56 27 M230.56 27 C263.06 36.7, 263.45 37.7, 230.56 45 M230.56 27 C262.77 34.43, 265.27 33.84, 230.56 45 M230.56 45 C207.96 49.11, 189 56.81, 165 61 M230.56 45 C216.3 48.17, 202.3 52.86, 165 61 M165 61 C132.97 70.5, 133.69 69.94, 99 61 M165 61 C132.45 68.77, 130.46 67.71, 99 61 M99 61 C73.14 57.52, 49.66 48.73, 33 45 M99 61 C76.45 55.22, 53.88 49.75, 33 45 M33 45 C-1.17 37.59, 0.65 37.92, 33 27 M33 45 C1.48 33.86, 0.55 37.62, 33 27 M33 27 C53.22 19.88, 73.56 14.62, 99 9 M33 27 C51.63 21.57, 68.25 16.65, 99 9 M99 9 C131.83 0.42, 131.24 -0.08, 165 9 M99 9 C133.84 2.23, 130.98 -1.21, 165 9" stroke="#e6961e" stroke-width="1" fill="none"></path></g><g transform="translate(638.6883299402068 193.66297304222525) rotate(0 52.95995330810547 12.5)"><text x="52.95995330810547" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Edit mode?</text></g><g stroke-linecap="round" transform="translate(559.7593977502654 758.051828022694) rotate(0 131.77777099609375 30)"><path d="M15 0 C71.79 -4.28, 131.54 -0.57, 248.56 0 C257.86 -0.14, 261.09 3.7, 263.56 15 C264.38 20.23, 262.6 26.33, 263.56 45 C264.21 52.12, 258.56 57.89, 248.56 60 C159.17 59.91, 74.27 59.54, 15 60 C1.59 58.64, -1.63 54.26, 0 45 C2.19 39.11, -1.51 28.86, 0 15 C-3.6 3.29, 8.17 3.44, 15 0" stroke="none" stroke-width="0" fill="#ffc9c9"></path><path d="M15 0 C89.38 2.7, 165.48 1.14, 248.56 0 M15 0 C71.68 -2.06, 127.12 -0.55, 248.56 0 M248.56 0 C258.06 0.7, 263.45 6.7, 263.56 15 M248.56 0 C257.77 -1.57, 265.27 2.84, 263.56 15 M263.56 15 C262.12 23.85, 264.32 36.07, 263.56 45 M263.56 15 C263.5 20.88, 263.83 28.62, 263.56 45 M263.56 45 C264.53 55.5, 260.24 59.94, 248.56 60 M263.56 45 C264.01 53.77, 257.02 57.71, 248.56 60 M248.56 60 C161.73 62.85, 76.85 60.37, 15 60 M248.56 60 C167.46 58.55, 86.45 58.64, 15 60 M15 60 C3.83 61.59, 0.65 56.92, 0 45 M15 60 C6.48 57.86, 0.55 56.62, 0 45 M0 45 C0.1 33.91, 0.2 24.97, 0 15 M0 45 C1.02 36.06, -0.07 27.92, 0 15 M0 15 C-0.17 5.42, 4.24 -0.08, 15 0 M0 15 C1.84 7.23, 3.98 -1.21, 15 0" stroke="#e03131" stroke-width="1" fill="none"></path></g><g transform="translate(570.7172529748748 775.551828022694) rotate(0 120.81991577148438 12.5)"><text x="120.81991577148438" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Generate code with LLM</text></g><g stroke-linecap="round" transform="translate(559.7593977502654 858.64773530204) rotate(0 131.77777099609375 30)"><path d="M15 0 C80.96 1.7, 147.75 -2.53, 248.56 0 C257.63 1.99, 266.28 2.75, 263.56 15 C261.71 25.01, 260.24 35.85, 263.56 45 C264.39 55.11, 256.96 62.1, 248.56 60 C158.37 55.31, 75.21 60.34, 15 60 C2.08 62.38, -3.06 53.52, 0 45 C2.89 32.7, -0.64 25.26, 0 15 C2.9 1.86, 4.93 0.73, 15 0" stroke="none" stroke-width="0" fill="#ffc9c9"></path><path d="M15 0 C80.31 1.21, 148.21 1.45, 248.56 0 M15 0 C91.21 -0.38, 166.82 0.04, 248.56 0 M248.56 0 C258.65 0.06, 263.53 4.01, 263.56 15 M248.56 0 C259.57 -1.44, 265.34 6.24, 263.56 15 M263.56 15 C264.08 22.98, 262.26 34.38, 263.56 45 M263.56 15 C263.27 26.73, 264.26 37.32, 263.56 45 M263.56 45 C263.54 55.38, 258.06 60.98, 248.56 60 M263.56 45 C264.36 55.03, 260.06 60.95, 248.56 60 M248.56 60 C198.34 61.56, 148.56 59.17, 15 60 M248.56 60 C185.95 60.25, 121.21 59.37, 15 60 M15 60 C4.62 59.12, -0.99 53.61, 0 45 M15 60 C6.13 60.9, -2.18 54.6, 0 45 M0 45 C0.73 36.66, -1.69 27.87, 0 15 M0 45 C-0.17 38.9, -0.47 31.65, 0 15 M0 15 C0.74 5.14, 3.76 -0.46, 15 0 M0 15 C0.51 4.43, 3.86 -0.06, 15 0" stroke="#e03131" stroke-width="1" fill="none"></path></g><g transform="translate(601.5172560266326 876.14773530204) rotate(0 90.01991271972656 12.5)"><text x="90.01991271972656" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Write files to disk</text></g><g stroke-linecap="round" transform="translate(559.7593977502654 958.0518890578503) rotate(0 131.77777099609375 29.999999999999943)"><path d="M15 0 C93.76 0.28, 172.22 -0.4, 248.56 0 C256.48 -3.06, 265.65 8.28, 263.56 15 C260.42 21.58, 263.02 28.39, 263.56 45 C260.44 53.36, 255.24 57.21, 248.56 60 C156.17 62.77, 65.4 63.39, 15 60 C3.43 60.83, 0.44 54.28, 0 45 C-0.49 37.61, 0.67 34.68, 0 15 C-3.5 8.36, 2.14 -2.42, 15 0" stroke="none" stroke-width="0" fill="#ffc9c9"></path><path d="M15 0 C80.7 2.58, 145.31 2.38, 248.56 0 M15 0 C73.87 -1.75, 131.92 -2.07, 248.56 0 M248.56 0 C260.14 -0.51, 265.5 4.95, 263.56 15 M248.56 0 C257.68 -0.06, 263.25 3.87, 263.56 15 M263.56 15 C264.59 21.29, 264.95 28.47, 263.56 45 M263.56 15 C264.49 24.55, 264.05 33.49, 263.56 45 M263.56 45 C263.3 56.4, 256.99 60.76, 248.56 60 M263.56 45 C264.61 57.23, 256.9 60.95, 248.56 60 M248.56 60 C179.83 59.43, 111.68 57.8, 15 60 M248.56 60 C172.32 61.76, 97.23 61.81, 15 60 M15 60 C5.81 61, -1.07 55.49, 0 45 M15 60 C5.93 57.85, -1 56.13, 0 45 M0 45 C1.64 37.59, -1.79 33.22, 0 15 M0 45 C-1.25 37.63, 0.4 32.29, 0 15 M0 15 C1.31 5.08, 5.58 0.05, 15 0 M0 15 C0.88 6.67, 2.72 -0.72, 15 0" stroke="#e03131" stroke-width="1" fill="none"></path></g><g transform="translate(590.0172712854217 975.5518890578503) rotate(0 101.5198974609375 12.5)"><text x="101.5198974609375" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Component processed</text></g><g mask="url(#mask-match-to-complete)" stroke-linecap="round"><g transform="translate(244.4694547689763 453.2768674853473) rotate(0 0.026610624536800742 31.596287982697845)"><path d="M0.16 1 C0.24 11.73, 0.15 53.47, 0.2 63.77 M-1.21 0.47 C-1.26 10.91, -0.86 51.37, -0.67 61.95" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(244.4694547689763 453.2768674853473) rotate(0 0.026610624536800742 31.596287982697845)"><path d="M-9.53 38.58 C-5.51 45.35, -3.73 52.34, -0.67 61.95 M-9.53 38.58 C-6.76 44.68, -5.31 51.89, -0.67 61.95" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(244.4694547689763 453.2768674853473) rotate(0 0.026610624536800742 31.596287982697845)"><path d="M7.57 38.35 C6.81 45.21, 3.81 52.26, -0.67 61.95 M7.57 38.35 C5.74 44.51, 2.57 51.78, -0.67 61.95" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask id="mask-match-to-complete"><rect x="0" y="0" fill="#fff" width="344.5226760180499" height="616.469443450743"></rect><rect x="206.306093469685" y="472.37315546804507" fill="#000" width="76.37994384765625" height="25" opacity="1"></rect></mask><g transform="translate(206.30609346968498 472.37315546804507) rotate(0 37.65874408399293 13.02644847230053)"><text x="38.189971923828125" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">All done</text></g><g stroke-opacity="0.4" fill-opacity="0.4" stroke-linecap="round" transform="translate(451.5371687463591 291.38517152855337) rotate(0 240 207.33334350585938)"><path d="M32 0 C151.41 0.61, 271.35 -2.1, 448 0 C468.41 1.99, 482.72 8.42, 480 32 C475.97 162.53, 475.01 293.59, 480 382.67 C480.84 404.11, 467.73 416.76, 448 414.67 C289.78 410.64, 136.06 413.85, 32 414.67 C7.75 417.05, -3.06 402.52, 0 382.67 C5.17 256.8, 2.88 134.08, 0 32 C2.9 7.53, 10.6 0.73, 32 0" stroke="none" stroke-width="0" fill="#f5f5f5"></path><path d="M32 0 C149.21 1.44, 268.08 1.59, 448 0 M32 0 C167.88 -0.48, 303.37 -0.21, 448 0 M448 0 C469.43 0.06, 479.97 9.67, 480 32 M448 0 C470.35 -1.44, 481.78 11.9, 480 32 M480 32 C481.97 144.8, 480.79 259.82, 480 382.67 M480 32 C480.01 158.48, 480.65 284.22, 480 382.67 M480 382.67 C479.99 404.38, 468.84 415.65, 448 414.67 M480 382.67 C480.8 404.03, 470.84 415.61, 448 414.67 M448 414.67 C358.23 415.8, 268.73 414.27, 32 414.67 M448 414.67 C335.61 414.82, 221.86 414.26, 32 414.67 M32 414.67 C10.29 413.79, -0.99 402.61, 0 382.67 M32 414.67 C11.8 415.57, -2.18 403.6, 0 382.67 M0 382.67 C0.34 284.07, -1.24 185.18, 0 32 M0 382.67 C0.09 301.65, -0.11 219.89, 0 32 M0 32 C0.74 10.81, 9.42 -0.46, 32 0 M0 32 C0.51 10.1, 9.53 -0.06, 32 0" stroke="#999999" stroke-width="1" fill="none"></path></g><g transform="translate(599.6254772544148 296.38517152855337) rotate(0 95.47991943359375 12.5)"><text x="95.47991943359375" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Resource Gathering</text></g><g stroke-linecap="round" transform="translate(467.9816267541716 347.16297304222525) rotate(0 100.22222900390625 25)"><path d="M12.5 0 C61.32 2.3, 111.13 -2.71, 187.94 0 C195.35 1.99, 203.17 1.92, 200.44 12.5 C198.66 20.64, 197.19 29.61, 200.44 37.5 C201.28 45.94, 194.68 52.1, 187.94 50 C119.27 45.05, 58.93 51.01, 12.5 50 C1.25 52.38, -3.06 44.36, 0 37.5 C2.81 26.98, -0.72 21.32, 0 12.5 C2.9 1.03, 4.1 0.73, 12.5 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M12.5 0 C61.23 1.05, 113.02 1.33, 187.94 0 M12.5 0 C69.69 -0.32, 126.19 0.19, 187.94 0 M187.94 0 C196.37 0.06, 200.41 3.17, 200.44 12.5 M187.94 0 C197.29 -1.44, 202.23 5.4, 200.44 12.5 M200.44 12.5 C200.93 18.85, 199.11 28.63, 200.44 37.5 M200.44 12.5 C200.16 22.44, 201.14 31.24, 200.44 37.5 M200.44 37.5 C200.43 46.21, 195.78 50.98, 187.94 50 M200.44 37.5 C201.25 45.87, 197.79 50.95, 187.94 50 M187.94 50 C150.35 51.77, 113.26 48.94, 12.5 50 M187.94 50 C141.25 50.3, 92.03 49.26, 12.5 50 M12.5 50 C3.79 49.12, -0.99 44.44, 0 37.5 M12.5 50 C5.3 50.9, -2.18 45.43, 0 37.5 M0 37.5 C0.73 30.57, -1.69 23.18, 0 12.5 M0 37.5 C-0.18 32.57, -0.48 26.48, 0 12.5 M0 12.5 C0.74 4.31, 2.92 -0.46, 12.5 0 M0 12.5 C0.51 3.6, 3.03 -0.06, 12.5 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(479.2121624350788 359.66297304222525) rotate(0 92.55992126464844 12.5)"><text x="92.55992126464844" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Read existing code</text></g><g stroke-linecap="round" transform="translate(721.7593367151092 341.3852020461315) rotate(0 84.888916015625 30)"><path d="M15 0 C62.12 1.44, 108.88 0.63, 154.78 0 C162.71 -3.06, 171.87 8.28, 169.78 15 C166.65 21.58, 169.24 28.39, 169.78 45 C166.66 53.36, 161.47 57.21, 154.78 60 C98.93 62.92, 44.99 63.65, 15 60 C3.43 60.83, 0.44 54.28, 0 45 C-0.49 37.61, 0.67 34.68, 0 15 C-3.5 8.36, 2.14 -2.42, 15 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M15 0 C55.01 2.63, 93.74 2.39, 154.78 0 M15 0 C50.57 -1.17, 85.17 -1.56, 154.78 0 M154.78 0 C166.37 -0.51, 171.72 4.95, 169.78 15 M154.78 0 C163.9 -0.06, 169.47 3.87, 169.78 15 M169.78 15 C170.81 21.29, 171.17 28.47, 169.78 45 M169.78 15 C170.71 24.55, 170.27 33.49, 169.78 45 M169.78 45 C169.52 56.4, 163.21 60.76, 154.78 60 M169.78 45 C170.83 57.23, 163.12 60.95, 154.78 60 M154.78 60 C113.65 60.15, 73.2 58.22, 15 60 M154.78 60 C109.04 61.22, 64.66 61.28, 15 60 M15 60 C5.81 61, -1.07 55.49, 0 45 M15 60 C5.93 57.85, -1 56.13, 0 45 M0 45 C1.64 37.59, -1.79 33.22, 0 15 M0 45 C-1.25 37.63, 0.4 32.29, 0 15 M0 15 C1.31 5.08, 5.58 0.05, 15 0 M0 15 C0.88 6.67, 2.72 -0.72, 15 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(739.3965496421101 346.3852020461315) rotate(0 70.81993103027344 25)"><text x="70.81993103027344" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Begin resource</text><text x="70.81993103027344" y="42.62" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">gathering</text></g><g stroke-linecap="round" transform="translate(592.2037947229217 449.3852020461315) rotate(0 100 25)"><path d="M12.5 0 C82.7 -2.89, 150.28 3.2, 187.5 0 C195.56 0.82, 197.95 6.42, 200 12.5 C203.79 20.75, 202.46 25.37, 200 37.5 C197.48 46.64, 194.84 52.93, 187.5 50 C127.37 46.01, 66.82 48.61, 12.5 50 C2.55 46.5, 0.21 42.54, 0 37.5 C2.9 32.62, -0.92 21.96, 0 12.5 C2.49 5.43, 6.39 -3.24, 12.5 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M12.5 0 C65.65 -0.05, 117.1 0.67, 187.5 0 M12.5 0 C59.84 -1.43, 106.53 -0.41, 187.5 0 M187.5 0 C194.93 -0.42, 201.95 5.21, 200 12.5 M187.5 0 C195.14 -1.31, 198.62 2.03, 200 12.5 M200 12.5 C201.21 22.4, 198.49 30.76, 200 37.5 M200 12.5 C199.26 20.7, 200.99 29.45, 200 37.5 M200 37.5 C199.29 44.43, 194.32 51.31, 187.5 50 M200 37.5 C198.17 47.69, 194.2 48.73, 187.5 50 M187.5 50 C144.74 51.8, 104.26 52, 12.5 50 M187.5 50 C149 49.46, 110.87 49.36, 12.5 50 M12.5 50 C2.27 48.66, 1.24 46.61, 0 37.5 M12.5 50 C4.22 48.91, 0.46 45.83, 0 37.5 M0 37.5 C2.05 27.64, 1.86 21.18, 0 12.5 M0 37.5 C0.32 32.56, -0.25 26.43, 0 12.5 M0 12.5 C0.49 3.8, 2.52 0.82, 12.5 0 M0 12.5 C1.96 5.35, 2.95 0.8, 12.5 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(605.7720226645711 449.3852020461315) rotate(0 90 25)"><text x="90" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Read component </text><text x="90" y="42.62" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">resources</text></g><g stroke-linecap="round" transform="translate(477.31493974245285 540.4962860305066) rotate(0 80 25)"><path d="M12.5 0 C43.65 -4.38, 78.31 0.01, 147.5 0 C155.14 -0.14, 157.54 2.87, 160 12.5 C160.85 16.7, 159.07 21.77, 160 37.5 C160.66 42.95, 155.83 47.89, 147.5 50 C94.58 49.29, 46.99 48.85, 12.5 50 C0.76 48.64, -1.63 45.09, 0 37.5 C2.2 32.69, -1.5 23.52, 0 12.5 C-3.6 2.46, 7.33 3.44, 12.5 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M12.5 0 C54.58 2.64, 98.7 0.78, 147.5 0 M12.5 0 C45.63 -1.76, 77.28 0.03, 147.5 0 M147.5 0 C155.34 0.7, 159.9 5.86, 160 12.5 M147.5 0 C155.04 -1.57, 161.72 2.01, 160 12.5 M160 12.5 C158.57 19.74, 160.77 30.34, 160 37.5 M160 12.5 C159.99 17.29, 160.32 23.94, 160 37.5 M160 37.5 C160.97 46.33, 157.52 49.94, 147.5 50 M160 37.5 C160.45 44.6, 154.3 47.71, 147.5 50 M147.5 50 C96.47 52.79, 47.75 49.85, 12.5 50 M147.5 50 C100.78 49.17, 54.17 49.28, 12.5 50 M12.5 50 C3 51.59, 0.65 47.75, 0 37.5 M12.5 50 C5.65 47.86, 0.55 47.46, 0 37.5 M0 37.5 C0.06 27.94, 0.15 20.54, 0 12.5 M0 37.5 C0.98 29.9, -0.1 23.1, 0 12.5 M0 12.5 C-0.17 4.59, 3.41 -0.08, 12.5 0 M0 12.5 C1.84 6.4, 3.15 -1.21, 12.5 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(491.88316768410226 540.4962860305066) rotate(0 69 25)"><text x="69" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Component </text><text x="69" y="42.62" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">spec &amp; docs</text></g><g stroke-linecap="round" transform="translate(741.5371687463592 539.1629730422253) rotate(0 80 25)"><path d="M12.5 0 C49.61 2.49, 87.7 -2.52, 147.5 0 C154.91 1.99, 162.72 1.92, 160 12.5 C158.22 20.64, 156.75 29.61, 160 37.5 C160.84 45.94, 154.23 52.1, 147.5 50 C94.08 45.47, 48.99 51.43, 12.5 50 C1.25 52.38, -3.06 44.36, 0 37.5 C2.81 26.98, -0.72 21.32, 0 12.5 C2.9 1.03, 4.1 0.73, 12.5 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M12.5 0 C49.78 0.78, 90.13 1.06, 147.5 0 M12.5 0 C56.48 -0.22, 99.75 0.29, 147.5 0 M147.5 0 C155.93 0.06, 159.97 3.17, 160 12.5 M147.5 0 C156.85 -1.44, 161.78 5.4, 160 12.5 M160 12.5 C160.48 18.85, 158.66 28.63, 160 37.5 M160 12.5 C159.71 22.44, 160.7 31.24, 160 37.5 M160 37.5 C159.99 46.21, 155.34 50.98, 147.5 50 M160 37.5 C160.8 45.87, 157.34 50.95, 147.5 50 M147.5 50 C118.65 51.72, 90.31 48.89, 12.5 50 M147.5 50 C111.78 50.3, 73.54 49.26, 12.5 50 M12.5 50 C3.79 49.12, -0.99 44.44, 0 37.5 M12.5 50 C5.3 50.9, -2.18 45.43, 0 37.5 M0 37.5 C0.73 30.57, -1.69 23.18, 0 12.5 M0 37.5 C-0.18 32.57, -0.48 26.48, 0 12.5 M0 12.5 C0.74 4.31, 2.92 -0.46, 12.5 0 M0 12.5 C0.51 3.6, 3.03 -0.06, 12.5 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(750.1053966880086 539.1629730422253) rotate(0 75 25)"><text x="75" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Dependency </text><text x="75" y="42.62" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">specs</text></g><g stroke-linecap="round" transform="translate(477.31493974245285 638.940744038319) rotate(0 80 25)"><path d="M12.5 0 C58 1.5, 103.16 0.69, 147.5 0 C153.76 -3.06, 162.09 7.45, 160 12.5 C156.81 18, 159.41 23.73, 160 37.5 C156.88 44.19, 152.52 47.21, 147.5 50 C93.52 52.9, 41.45 53.63, 12.5 50 C2.6 50.83, 0.44 45.11, 0 37.5 C-0.48 31.15, 0.68 29.28, 0 12.5 C-3.5 7.52, 1.3 -2.42, 12.5 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M12.5 0 C51.19 2.61, 88.6 2.37, 147.5 0 M12.5 0 C46.88 -1.13, 80.28 -1.52, 147.5 0 M147.5 0 C157.42 -0.51, 161.94 4.12, 160 12.5 M147.5 0 C154.95 -0.06, 159.7 3.04, 160 12.5 M160 12.5 C161.02 17.72, 161.38 23.83, 160 37.5 M160 12.5 C160.93 20.46, 160.49 27.82, 160 37.5 M160 37.5 C159.74 47.24, 154.26 50.76, 147.5 50 M160 37.5 C161.05 48.06, 154.18 50.95, 147.5 50 M147.5 50 C107.78 50.2, 68.74 48.27, 12.5 50 M147.5 50 C103.32 51.18, 60.49 51.24, 12.5 50 M12.5 50 C4.97 51, -1.07 46.32, 0 37.5 M12.5 50 C5.1 47.85, -1 46.96, 0 37.5 M0 37.5 C1.61 31.15, -1.82 27.85, 0 12.5 M0 37.5 C-1.2 31.21, 0.45 26.94, 0 12.5 M0 12.5 C1.31 4.25, 4.75 0.05, 12.5 0 M0 12.5 C0.88 5.84, 1.88 -0.72, 12.5 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(491.88316768410226 638.940744038319) rotate(0 69 25)"><text x="69" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Reference </text><text x="69" y="42.62" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">documentation</text></g><g stroke-linecap="round" transform="translate(741.5371687463592 638.4962860305066) rotate(0 80 25)"><path d="M12.5 0 C66.77 -2.97, 118.42 3.11, 147.5 0 C155.56 0.82, 157.95 6.42, 160 12.5 C163.79 20.75, 162.46 25.37, 160 37.5 C157.48 46.64, 154.84 52.93, 147.5 50 C101.04 46.14, 54.17 48.74, 12.5 50 C2.55 46.5, 0.21 42.54, 0 37.5 C2.9 32.62, -0.92 21.96, 0 12.5 C2.49 5.43, 6.39 -3.24, 12.5 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M12.5 0 C53.8 0.16, 93.4 0.89, 147.5 0 M12.5 0 C49.07 -1.14, 84.98 -0.12, 147.5 0 M147.5 0 C154.93 -0.42, 161.95 5.21, 160 12.5 M147.5 0 C155.14 -1.31, 158.62 2.03, 160 12.5 M160 12.5 C161.21 22.4, 158.49 30.76, 160 37.5 M160 12.5 C159.26 20.7, 160.99 29.45, 160 37.5 M160 37.5 C159.29 44.43, 154.32 51.31, 147.5 50 M160 37.5 C158.17 47.69, 154.2 48.73, 147.5 50 M147.5 50 C114.46 51.58, 83.7 51.78, 12.5 50 M147.5 50 C117.75 49.77, 88.38 49.66, 12.5 50 M12.5 50 C2.27 48.66, 1.24 46.61, 0 37.5 M12.5 50 C4.22 48.91, 0.46 45.83, 0 37.5 M0 37.5 C2.05 27.64, 1.86 21.18, 0 12.5 M0 37.5 C0.32 32.56, -0.25 26.43, 0 12.5 M0 12.5 C0.49 3.8, 2.52 0.82, 12.5 0 M0 12.5 C1.96 5.35, 2.95 0.8, 12.5 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(750.1053966880086 638.4962860305066) rotate(0 75 25)"><text x="75" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Implementation </text><text x="75" y="42.62" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">guidance</text></g><g stroke-linecap="round"><g transform="translate(577.297205795076 537.079351806472) rotate(0 23.652024911843625 -18.301718806925294)"><path d="M-0.28 0.48 C7.7 -5.76, 39.46 -30.75, 47.47 -36.92 M0.58 0.25 C8.54 -5.69, 39.28 -30.36, 47.12 -36.38" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(577.297205795076 537.079351806472) rotate(0 23.652024911843625 -18.301718806925294)"><path d="M33.94 -15.14 C37.64 -19.52, 39.13 -23.71, 47.12 -36.38 M33.94 -15.14 C37.93 -21.52, 42.54 -28.91, 47.12 -36.38" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(577.297205795076 537.079351806472) rotate(0 23.652024911843625 -18.301718806925294)"><path d="M23.37 -28.58 C29.48 -29.95, 33.31 -31.16, 47.12 -36.38 M23.37 -28.58 C30.67 -30.78, 38.61 -33.95, 47.12 -36.38" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(631.3282089412908 635.8815403511139) rotate(0 20.26941245941947 -66.5208193198423)"><path d="M-0.69 1.11 C6.05 -20.9, 34.41 -110.83, 41.1 -133.18 M1.15 0.65 C7.72 -21.08, 33.67 -109.67, 40.45 -131.72" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(631.3282089412908 635.8815403511139) rotate(0 20.26941245941947 -66.5208193198423)"><path d="M41.91 -106.76 C43.47 -114.72, 40.86 -126.33, 40.45 -131.72 M41.91 -106.76 C41.9 -114.11, 41.38 -122.22, 40.45 -131.72" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(631.3282089412908 635.8815403511139) rotate(0 20.26941245941947 -66.5208193198423)"><path d="M25.52 -111.66 C32.88 -117.78, 36.11 -127.65, 40.45 -131.72 M25.52 -111.66 C30.47 -117.48, 34.92 -124.09, 40.45 -131.72" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(788.8566886923084 535.5616830183576) rotate(0 -16.92041280379169 -16.757885960170768)"><path d="M0.49 0.35 C-5.32 -5.31, -28.6 -28.09, -34.39 -33.77 M0.09 0.05 C-5.62 -5.56, -27.9 -27.65, -33.44 -33.2" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(788.8566886923084 535.5616830183576) rotate(0 -16.92041280379169 -16.757885960170768)"><path d="M-11.83 -23.18 C-19.73 -28.03, -29.33 -31.75, -33.44 -33.2 M-11.83 -23.18 C-17.8 -25.89, -22.77 -28.52, -33.44 -33.2" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(788.8566886923084 535.5616830183576) rotate(0 -16.92041280379169 -16.757885960170768)"><path d="M-23.33 -11.64 C-26.72 -21.08, -31.79 -29.35, -33.44 -33.2 M-23.33 -11.64 C-26.29 -17.37, -28.27 -23.01, -33.44 -33.2" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(747.6382411037614 634.3061006956566) rotate(0 -22.07488969747118 -65.31367786961357)"><path d="M-0.74 0.56 C-8.1 -21.04, -36.36 -108.31, -43.71 -130.01 M1.07 -0.19 C-6.45 -22.1, -36.59 -109.93, -44.43 -131.8" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(747.6382411037614 634.3061006956566) rotate(0 -22.07488969747118 -65.31367786961357)"><path d="M-28.61 -112.45 C-32.95 -118.36, -38.2 -126.78, -44.43 -131.8 M-28.61 -112.45 C-33.99 -119.38, -40.66 -126.5, -44.43 -131.8" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(747.6382411037614 634.3061006956566) rotate(0 -22.07488969747118 -65.31367786961357)"><path d="M-44.75 -106.81 C-43.62 -114.52, -43.41 -124.85, -44.43 -131.8 M-44.75 -106.81 C-43.95 -116.03, -44.41 -125.31, -44.43 -131.8" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(672.5452318554102 369.40700007883356) rotate(0 22.047413104457576 0.2549443526448272)"><path d="M0.18 -0.12 C7.48 -0.15, 36.57 0.23, 43.94 0.25 M-0.39 -0.66 C6.82 -0.65, 36 0.65, 43.44 0.82" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(672.5452318554102 369.40700007883356) rotate(0 22.047413104457576 0.2549443526448272)"><path d="M22.47 7.64 C28.98 5.13, 35.48 3.78, 43.44 0.82 M22.47 7.64 C26.38 6.22, 31.74 4.72, 43.44 0.82" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(672.5452318554102 369.40700007883356) rotate(0 22.047413104457576 0.2549443526448272)"><path d="M22.99 -7.43 C29.39 -5.08, 35.73 -1.58, 43.44 0.82 M22.99 -7.43 C26.78 -5.7, 32.03 -4.04, 43.44 0.82" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(766.9142380058499 407.3858220720863) rotate(0 -13.870632202009574 18.024011650442986)"><path d="M0.43 -0.11 C-4.2 5.83, -23.16 30.08, -27.93 36.18 M-0.02 -0.64 C-4.71 5.36, -23.94 29.23, -28.45 35.28" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(766.9142380058499 407.3858220720863) rotate(0 -13.870632202009574 18.024011650442986)"><path d="M-21.44 13.64 C-23.41 19.12, -24.86 24.43, -28.45 35.28 M-21.44 13.64 C-23.96 21.62, -26.69 30.23, -28.45 35.28" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(766.9142380058499 407.3858220720863) rotate(0 -13.870632202009574 18.024011650442986)"><path d="M-9.18 23.21 C-14.47 26.18, -19.2 28.93, -28.45 35.28 M-9.18 23.21 C-16.37 27.61, -23.74 32.61, -28.45 35.28" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g mask="url(#mask-Lm5YCicKEwjG6SrJlxhgr)" stroke-linecap="round"><g transform="translate(587.1830799322145 226.11675585789465) rotate(0 -42.36044623557689 55.29579976093365)"><path d="M0.04 0.3 C-9.28 5.91, -41.91 15.4, -56.22 33.71 C-70.52 52.01, -81.19 97.27, -85.81 110.15 M-1.39 -0.59 C-10.32 4.64, -40.26 13.12, -53.94 31.75 C-67.62 50.39, -78.6 97.81, -83.49 111.24" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(587.1830799322145 226.11675585789465) rotate(0 -42.36044623557689 55.29579976093365)"><path d="M-84.83 86.28 C-83.95 91.84, -83.53 98.36, -83.49 111.24 M-84.83 86.28 C-83.57 93.64, -83.68 99.71, -83.49 111.24" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(587.1830799322145 226.11675585789465) rotate(0 -42.36044623557689 55.29579976093365)"><path d="M-68.47 91.25 C-72.14 95.43, -76.28 100.57, -83.49 111.24 M-68.47 91.25 C-71.55 97.36, -75.97 102.12, -83.49 111.24" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask id="mask-Lm5YCicKEwjG6SrJlxhgr"><rect x="0" y="0" fill="#fff" width="771.9039724033682" height="436.70835537976194"></rect><rect x="515.9622540642613" y="246.99629244131904" fill="#000" width="31.679977416992188" height="25" opacity="1"></rect></mask><g transform="translate(515.9622540642614 246.99629244131904) rotate(0 28.336784333177008 34.44745596144611)"><text x="15.839988708496094" y="17.619999999999997" font-family="Excalifont, Xiaolai, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Yes</text></g><g mask="url(#mask-TKV39LSOmiDZlottftzrO)" stroke-linecap="round"><g transform="translate(788.5733046914756 226.18004089530467) rotate(0 37.655052066574456 54.28671802577762)"><path d="M-0.64 -0.02 C7.63 6.78, 36.86 23.6, 49.6 41.58 C62.34 59.56, 71.53 96.69, 75.81 107.86 M1.23 -1.07 C9.31 5.8, 36.15 24.48, 48.49 42.79 C60.84 61.1, 70.8 97.64, 75.3 108.8" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(788.5733046914756 226.18004089530467) rotate(0 37.655052066574456 54.28671802577762)"><path d="M59.54 89.4 C64.35 94.79, 68.05 101.91, 75.3 108.8 M59.54 89.4 C62.97 94.5, 67.33 98.83, 75.3 108.8" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(788.5733046914756 226.18004089530467) rotate(0 37.655052066574456 54.28671802577762)"><path d="M75.7 83.81 C75.72 90.78, 74.59 99.58, 75.3 108.8 M75.7 83.81 C75.24 90.26, 75.71 95.94, 75.3 108.8" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask id="mask-TKV39LSOmiDZlottftzrO"><rect x="0" y="0" fill="#fff" width="963.8834088246246" height="434.7534769468599"></rect><rect x="826.1488690544957" y="255.88517793936592" fill="#000" width="24.639999389648438" height="25" opacity="1"></rect></mask><g transform="translate(826.1488690544958 255.88517793936592) rotate(0 0.007685476727885998 24.16045343027622)"><text x="12.319999694824219" y="17.619999999999997" font-family="Excalifont, Xiaolai, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">No</text></g><g stroke-linecap="round"><g transform="translate(689.4917365157881 126.52376499919362) rotate(0 1.7958314367958224 20.70321010189069)"><path d="M0.38 0.36 C0.89 7.36, 2.64 34.72, 3.16 41.62 M-0.08 0.06 C0.59 6.94, 3.64 33.97, 4.17 40.76" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(689.4917365157881 126.52376499919362) rotate(0 1.7958314367958224 20.70321010189069)"><path d="M-4.81 22.02 C-1.36 27.19, 1.24 33.82, 4.17 40.76 M-4.81 22.02 C-1.87 28.32, 1.42 35.38, 4.17 40.76" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(689.4917365157881 126.52376499919362) rotate(0 1.7958314367958224 20.70321010189069)"><path d="M9.34 20.63 C8.26 26.3, 6.34 33.36, 4.17 40.76 M9.34 20.63 C7.24 27.46, 5.51 35.01, 4.17 40.76" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g mask="url(#mask-ySSobv5QuYECoDtsy9PpX)" stroke-linecap="round"><g transform="translate(353.93296717084837 372.4962860305065) rotate(0 96.56316766324503 -147.86497758961605)"><path d="M0.18 0.14 C7.05 -9, 28.23 -8.9, 40.78 -55.49 C53.34 -102.08, 50.02 -242.15, 75.5 -279.4 C100.97 -316.66, 173.99 -279.05, 193.63 -279.02 M-1.18 -0.84 C5.63 -9.79, 27.03 -8.19, 40.2 -54.44 C53.37 -100.69, 52.16 -241.06, 77.85 -278.32 C103.53 -315.59, 175.26 -277.93, 194.31 -278.04" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(353.93296717084837 372.4962860305065) rotate(0 96.56316766324503 -147.86497758961605)"><path d="M169.46 -275.34 C176.25 -274.94, 181.01 -278.53, 194.31 -278.04 M169.46 -275.34 C176.39 -276.34, 183.14 -277.39, 194.31 -278.04" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(353.93296717084837 372.4962860305065) rotate(0 96.56316766324503 -147.86497758961605)"><path d="M173.54 -291.95 C179.16 -287.17, 182.84 -286.38, 194.31 -278.04 M173.54 -291.95 C179.52 -288.6, 185.2 -285.3, 194.31 -278.04" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask id="mask-ySSobv5QuYECoDtsy9PpX"><rect x="0" y="0" fill="#fff" width="646.7386537191085" height="751.4406552406429"></rect><rect x="391.46548362806755" y="188.16323247143862" fill="#000" width="31.679977416992188" height="25" opacity="1"></rect></mask><g transform="translate(391.4654836280676 188.16323247143856) rotate(0 59.03065120602585 36.46807596945186)"><text x="15.839988708496094" y="17.619999999999997" font-family="Excalifont, Xiaolai, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Yes</text></g><g mask="url(#mask-WM7UQjc4eu62cZzmhf5n0)" stroke-linecap="round"><g transform="translate(142.3507372175026 363.6073700148815) rotate(0 -10.829789214560108 -40.10570548388969)"><path d="M-0.76 -0.28 C-4.19 -5.44, -19.04 -16.42, -21.32 -29.88 C-23.59 -43.33, -15.75 -72.48, -14.43 -81.02" stroke="#1e1e1e" stroke-width="1.5" fill="none" stroke-dasharray="8 9"></path></g><g transform="translate(142.3507372175026 363.6073700148815) rotate(0 -10.829789214560108 -40.10570548388969)"><path d="M-10.77 -56.44 C-12.33 -61.77, -10.78 -68.39, -14.43 -81.02" stroke="#1e1e1e" stroke-width="1.5" fill="none"></path></g><g transform="translate(142.3507372175026 363.6073700148815) rotate(0 -10.829789214560108 -40.10570548388969)"><path d="M-27.42 -59.84 C-24.98 -64.25, -19.44 -70.06, -14.43 -81.02" stroke="#1e1e1e" stroke-width="1.5" fill="none"></path></g></g><mask id="mask-WM7UQjc4eu62cZzmhf5n0"><rect x="0" y="0" fill="#fff" width="264.0103156466228" height="543.8187809826609"></rect><rect x="71.73117496269879" y="320.05186638159523" fill="#000" width="97.91996765136719" height="25" opacity="1"></rect></mask><g transform="translate(71.73117496269879 320.0518663815952) rotate(0 59.37581271349091 2.904440693710825)"><text x="48.959983825683594" y="17.619999999999997" font-family="Excalifont, Xiaolai, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">No / Next</text></g><g stroke-linecap="round"><g transform="translate(253.15772335426308 82.27407546430463) rotate(0 0 12.000000000000007)"><path d="M-0.4 0.16 C-0.45 4.02, -0.15 19.68, 0 23.68 M0.39 -0.23 C0.25 3.93, -0.43 20.31, -0.43 24.22" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(253.15772335426308 82.27407546430463) rotate(0 0 12.000000000000007)"><path d="M-4.26 12.84 C-2.7 16.81, -1.9 21.29, -0.43 24.22 M-4.26 12.84 C-3.07 16.42, -1.9 20.48, -0.43 24.22" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(253.15772335426308 82.27407546430463) rotate(0 0 12.000000000000007)"><path d="M3.95 13.04 C2.65 16.91, 0.61 21.32, -0.43 24.22 M3.95 13.04 C2.39 16.59, 0.8 20.58, -0.43 24.22" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(247.9788666742792 279.3683124131073) rotate(0 -0.4695284676550955 16.043784082711113)"><path d="M0.39 -0.2 C0.31 5.2, -0.27 27.31, -0.42 32.62 M-0.07 -0.78 C-0.18 4.46, -0.49 26.46, -0.59 31.93" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(247.9788666742792 279.3683124131073) rotate(0 -0.4695284676550955 16.043784082711113)"><path d="M-5.84 16.76 C-4.5 22.13, -1.82 26.59, -0.59 31.93 M-5.84 16.76 C-4.73 19.97, -3.81 23.13, -0.59 31.93" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(247.9788666742792 279.3683124131073) rotate(0 -0.4695284676550955 16.043784082711113)"><path d="M5.14 16.93 C3.12 22.29, 2.44 26.7, -0.59 31.93 M5.14 16.93 C3.85 20.1, 2.37 23.22, -0.59 31.93" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(249.87168355568053 178.78838057344598) rotate(0 -0.01129442605027009 18.06975525044969)"><path d="M0.36 -0.03 C0.3 5.98, -0.26 29.68, -0.29 35.68 M-0.12 -0.52 C-0.28 5.57, -0.87 29.97, -0.85 36.15" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(249.87168355568053 178.78838057344598) rotate(0 -0.01129442605027009 18.06975525044969)"><path d="M-6.82 19.09 C-5.07 23.91, -3.93 30.01, -0.85 36.15 M-6.82 19.09 C-4.96 23.39, -3.7 28.4, -0.85 36.15" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(249.87168355568053 178.78838057344598) rotate(0 -0.01129442605027009 18.06975525044969)"><path d="M5.54 19.25 C3.47 24.06, 0.78 30.11, -0.85 36.15 M5.54 19.25 C3.99 23.51, 1.83 28.48, -0.85 36.15" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(696.6074381696501 708.2703275198544) rotate(0 0.6143259331372519 24.602363421909672)"><path d="M0.53 0.32 C0.77 8.45, 1.2 40.87, 1.32 49.08 M0.13 0 C0.33 8.2, 0.81 41.59, 0.94 49.71" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(696.6074381696501 708.2703275198544) rotate(0 0.6143259331372519 24.602363421909672)"><path d="M-7.83 26.72 C-4.79 33.16, -3.19 39.34, 0.94 49.71 M-7.83 26.72 C-4.75 35.61, -1.47 43.63, 0.94 49.71" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(696.6074381696501 708.2703275198544) rotate(0 0.6143259331372519 24.602363421909672)"><path d="M9 26.46 C7.42 33.05, 4.41 39.31, 0.94 49.71 M9 26.46 C5.87 35.42, 2.93 43.55, 0.94 49.71" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(691.5371283329548 818.6124398304876) rotate(0 -0.12294634761428824 19.43557794496104)"><path d="M-0.4 0.43 C-0.38 6.79, 0.29 32.28, 0.24 38.62 M0.4 0.18 C0.37 6.84, 0.07 32.74, 0.06 39.19" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(691.5371283329548 818.6124398304876) rotate(0 -0.12294634761428824 19.43557794496104)"><path d="M-6.46 20.88 C-3.48 27.75, -2.55 32.04, 0.06 39.19 M-6.46 20.88 C-4.82 25.13, -3.35 29.48, 0.06 39.19" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(691.5371283329548 818.6124398304876) rotate(0 -0.12294634761428824 19.43557794496104)"><path d="M6.84 20.98 C5.47 27.77, 2.05 32.03, 0.06 39.19 M6.84 20.98 C5.42 25.23, 3.82 29.56, 0.06 39.19" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(691.8518028174735 919.0995326811988) rotate(0 -0.8381155503968216 18.58260425712632)"><path d="M-0.21 -0.03 C-0.43 6.15, -0.99 30.91, -1.15 37.18 M0.68 -0.52 C0.43 5.74, -0.99 31.68, -1.31 37.89" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(691.8518028174735 919.0995326811988) rotate(0 -0.8381155503968216 18.58260425712632)"><path d="M-6.74 20.1 C-5.01 26.73, -3.19 32.46, -1.31 37.89 M-6.74 20.1 C-5.14 26.93, -2.49 33.37, -1.31 37.89" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(691.8518028174735 919.0995326811988) rotate(0 -0.8381155503968216 18.58260425712632)"><path d="M5.97 20.77 C3.6 27.16, 1.33 32.68, -1.31 37.89 M5.97 20.77 C2.79 27.3, 0.67 33.49, -1.31 37.89" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(548.923675917121 993.6301657036602) rotate(0 -267.2273578075334 -375.7997645617079)"><path d="M-0.69 -0.82 C-33.61 -9.93, -127.27 -16.54, -197.47 -55.22 C-267.67 -93.91, -365.9 -152.98, -421.89 -232.94 C-477.89 -312.9, -518.27 -450.05, -533.43 -534.99 C-548.6 -619.93, -529.27 -706.37, -512.88 -742.6 C-496.49 -778.83, -448.26 -750.9, -435.09 -752.37" stroke="#1e1e1e" stroke-width="1.5" fill="none" stroke-dasharray="8 9"></path></g><g transform="translate(548.923675917121 993.6301657036602) rotate(0 -267.2273578075334 -375.7997645617079)"><path d="M-459.84 -748.82 C-453.64 -749.6, -443.76 -752.13, -435.09 -752.37" stroke="#1e1e1e" stroke-width="1.5" fill="none"></path></g><g transform="translate(548.923675917121 993.6301657036602) rotate(0 -267.2273578075334 -375.7997645617079)"><path d="M-456.33 -765.56 C-451.28 -761.25, -442.47 -758.67, -435.09 -752.37" stroke="#1e1e1e" stroke-width="1.5" fill="none"></path></g></g><mask></mask></svg>

=== File: recipes/codebase_generator/recipes/generate_component_code.json ===
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "{% assign id_parts = component.id | split: '.' -%}{% assign path = id_parts | size | minus: 1 | join: '/' -%}{% assign id = id_parts | last -%}# Task\n\nYou are an expert developer. Based on the following specification{% if existing_code %} and existing code{% endif %}, generate code for the {{ component.id }} component of a larger project.\n\n## Specification\n<SPECIFICATION>\n{{ spec }}\n</SPECIFICATION>\n\n{% if existing_code %}## Existing Code\n\nThis is the prior version of the code and can be used for reference, however the specifications or dependencies may have changed, so it may need to be updated.\n\n<EXISTING_CODE>\n{{ existing_code }}\n</EXISTING_CODE>\n\n{% endif %}## Usage Documentation\n\nThis is the usage documentation that will be provided to callers of this component, it is critical that this is considered a contract and must be fulfilled as this is what is being promised from this component.\n\n<USAGE_DOCUMENTATION>\n{{ docs }}\n</USAGE_DOCUMENTATION>\n\n{% if dep_docs %}## Dependency Documentation\n\nIncludes documentation for internal dependencies.\n{% for dep_doc in dep_docs %}<DEPENDENCY_DOC>\n{{ dep_doc }}\n</DEPENDENCY_DOC>\n{% endfor %}\n{% endif %}{% if ref_docs %}# Reference Documentation\n\nIncludes additional documentation for external libraries that have been loaded into this project.\n{% for ref_doc in ref_docs %}<REFERENCE_DOC>\n{{ ref_doc }}\n</REFERENCE_DOC>\n{% endfor %}\n{% endif %}## Guidance\n\nEnsure the code follows the specification exactly, implements all required functionality, and adheres to the implementation philosophy described in the tags. Include appropriate error handling and type hints. The implementation should be minimal but complete.\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{ implementation_philosophy }}\n</IMPLEMENTATION_PHILOSOPHY>\n\n{% if dev_guide %}<DEV_GUIDE>\n{{ dev_guide }}\n</DEV_GUIDE>\n\n{% endif %}# Output\n\nGenerate the appropriate file(s) (if the specification defines multiple output files. Include the comment `# This file was generated by Codebase-Generator, do not edit directly` at the top of each file. MAKE SURE TO CREATE ALL FILES at once and return in the `files` collection). For example, {{ output_path }}/{{ path }}/{{ id }}.<ext>, {{ output_path }}/{{ path }}/<other files defined in specification>, etc.\n\n",
        "model": "{{ model }}",
        "output_format": "files",
        "output_key": "generated_files"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_files",
        "root": "{{ output_root }}"
      }
    }
  ]
}


=== File: recipes/codebase_generator/recipes/process_component.json ===
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "{{ edit }}",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ existing_code_root }}/{{ component.id | replace: '.', '/' }}.py",
                "content_key": "existing_code",
                "optional": true
              }
            }
          ]
        }
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/read_component_resources.json"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/generate_component_code.json"
      }
    }
  ]
}


=== File: recipes/codebase_generator/recipes/read_component_resources.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ project_blueprints_root }}/components/{{ component.id | replace: '.', '/' }}/{{ component.id | split: '.' | last }}_spec.md",
        "content_key": "spec"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{{ project_blueprints_root }}/components/{{ component.id | replace: '.', '/' }}/{{ component.id | split: '.' | last }}_docs.md",
        "content_key": "docs",
        "optional": true
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{% for dep in component.deps %}{{ project_blueprints_root }}/components/{{ dep | replace: '.', '/' }}/{{ dep | split: '.' | last }}_docs.md{% unless forloop.last %},{% endunless %}{% endfor %}",
        "content_key": "dep_docs",
        "merge_mode": "dict",
        "optional": true
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{% for ref in component.refs %}{{ refs_root }}/{{ ref }}{% unless forloop.last %},{% endunless %}{% endfor %}",
        "content_key": "ref_docs",
        "merge_mode": "dict",
        "optional": true
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
        "content_key": "implementation_philosophy"
      }
    },
    {
      "type": "conditional",
      "config": {
        "condition": "{% if dev_guide_path != 'none' %}true{% else %}false{% endif %}",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ dev_guide_path }}",
                "content_key": "dev_guide"
              }
            }
          ]
        }
      }
    }
  ]
}


=== File: recipes/codebase_generator/recipes/read_components.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ project_blueprints_root }}/components.json",
        "content_key": "components",
        "merge_mode": "dict"
      }
    }
  ]
}


