# Instructions for Testing the Blueprint Generator

## Run the Blueprint Generator

```bash
# From the repo root, run the blueprint generator with the test project
recipe-tool --execute recipes/experimental/blueprint_generator/build.json \
   raw_idea_path=blueprints/experimental/requirements_recipe_tool_ux.md \
   context_files=blueprints/experimental/vision_recipe_tool_ux.md \
   output_dir=output/blueprint_generator \
   model=openai/o4-mini
```
