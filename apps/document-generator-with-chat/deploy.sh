 #!/bin/bash
  # Read arguments to script: --name --resource-group --slot (slot is optional)
  echo ""
  echo "Starting deployment script..."
  if [[ $# -lt 2 ]]; then
    echo "Usage: $0 --name <app_name> --resource-group <resource_group> [--slot <slot_name>]"
    exit 1
  fi

  while [[ $# -gt 0 ]]; do
    case $1 in
      --name)
        app_name="$2"
        shift 2
        ;;
      --resource-group)
        resource_group="$2"
        shift 2
        ;;
      --slot)
        slot_name="$2"
        shift 2
        ;;
      *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
  done

  echo "App Name: $app_name"
  echo "Resource Group: $resource_group"
  if [[ "$slot_name" ]]; then
    echo "Slot Name: $slot_name"
  fi

  # Create deployment package
echo ""
echo "Remove existing deployment package if it exists..."
  if [[ -f deployment.zip ]]; then
    rm deployment.zip
    echo "Removed existing deployment.zip"
  fi

echo ""
echo "Creating deployment package..."
  zip -r deployment.zip . \
    -x "*.git*" \
    -x "*__pycache__*" \
    -x ".venv/*" \
    -x ".ruff*" \
    -x ".env*" \
    -x "*.log" \
    -x "Makefile" \
    -x "*.md" \
    -x "scripts/*" \
    -x "*.zip" \
    -x "deploy.sh" \
    -x "uv.lock" \
    -x "pyproject.toml" \
    -x "examples/Documentation*/" \
    -x "examples/scenario-[1-3,5]*/*" \
    -x "examples/*/*.json" \
    -x "examples/*/*.txt" \
    -x "examples/*/*.csv" \
    -x "logs/"


  echo "If ready to deploy, press 'Y'. Otherwise, press 'N' to cancel."
  read -n 1 -s response
  echo
  if [[ "$response" != "Y" ]]; then
    echo "Deployment cancelled."
    exit 1
  fi
  echo "Deployment confirmed. Proceeding..."

  # Deploy to Azure
  if [[ "$slot_name" ]]; then
  echo "Deploying to Azure slot... $app_name-$slot_name"
    az webapp deploy \
      --name "$app_name" \
      --resource-group "$resource_group" \
      --slot "$slot_name" \
      --src-path deployment.zip \
      --type zip
  else
    echo "Deploying to Azure... $app_name"
    az webapp deploy \
      --name "$app_name" \
      --resource-group "$resource_group" \
      --src-path deployment.zip \
      --type zip
  fi

  echo "Deployment complete!"