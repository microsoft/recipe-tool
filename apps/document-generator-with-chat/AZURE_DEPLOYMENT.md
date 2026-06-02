# Azure App Service Deployment - Quick Guide

Simple deployment guide for hosting the Document Generator on Azure App Service with managed identity.

## Prerequisites

- Azure subscription
- Azure OpenAI resource
- User-assigned managed identity (already created)

## Deployment Steps

### 1. Create App Service

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"** → **"Web App"**
3. Fill in:
   - **Name**: `document-generator-app` (or your choice)
   - **Runtime**: `Python 3.11`
   - **Operating System**: `Linux`
   - **Region**: Same as your Azure OpenAI resource
4. Click **"Review + create"** → **"Create"**

### 2. Secure with Microsoft Authentication (Recommended)

Secure your app before deployment to prevent unauthorized access:

#### A. Configure Authentication on Web App

1. In your web app resource, navigate to **"Settings"** → **"Authentication"**
2. Click **"Add identity provider"**
3. Set the following:
   - **Identity provider**: Microsoft
   - **Application (client) ID**: `<YOUR-APP-REGISTRATION-CLIENT-ID>`
   - **Allowed tenants**: `<YOUR-TENANT-ID>` (for single tenant access)
4. Click **"Add"**
5. Navigate to **"Overview"** → Note the **"Default domain"** (needed for next step)

#### B. Configure App Registration

1. Go to your app registration in Entra ID
2. Navigate to **"Manage"** → **"Authentication"**
3. Find **"Platform configurations"** → **"Single-page application"** → **"Redirect URIs"**
4. Click **"Add URI"**
5. Add a new entry using your default domain:
   ```
   https://<YOUR-DEFAULT-DOMAIN>/.auth/login/aad/callback
   ```
6. Click **"Save"**

**Note**: If you delete the web app later, remember to remove its redirect URI from the app registration to keep it clean.

### 3. Assign Managed Identity

1. Go to your new App Service
2. Left menu → **"Identity"**
3. **"User assigned"** tab → **"Add"**
4. Select your existing managed identity
5. Click **"Add"**

### 4. Grant Azure OpenAI Access to Managed Identity

**Critical Step**: The managed identity needs permissions to access your Azure OpenAI resource.

1. Go to your **Azure OpenAI resource** in the portal
2. Left menu → **"Access control (IAM)"**
3. Click **"Add"** → **"Add role assignment"**
4. **Role**: Select **"Cognitive Services OpenAI User"**
5. **Assign access to**: User assigned managed identity
6. **Members**: Select your managed identity (same one assigned to App Service)
7. Click **"Review + assign"** → **"Assign"**

**Note**: Role assignment can take 5-10 minutes to propagate. The app will fail with authentication errors until this completes.

### 5. Configure App Service

#### A. Set Startup Command

1. Left menu → **"Configuration"**
2. **"General settings"** tab
3. **Startup Command**: `python startup.py` (or adjust if your entry point is different)
   - This command runs your application when the App Service starts
   - Ensure `startup.py` is in the root of your deployment package
4. Click **"Save"**

#### B. Configure Environment Variables

1. **"Application settings"** tab
2. Click **"Advanced edit"**
3. Add these entries to the existing JSON array (don't replace the entire array):

```json
[
  {
    "name": "GRADIO_SERVER_NAME",
    "value": "0.0.0.0",
    "slotSetting": false
  },
  {
    "name": "GRADIO_SERVER_PORT",
    "value": "8000",
    "slotSetting": false
  },
  {
    "name": "SCM_DO_BUILD_DURING_DEPLOYMENT",
    "value": "true",
    "slotSetting": false
  },
  {
    "name": "LLM_PROVIDER",
    "value": "azure",
    "slotSetting": false
  },
  {
    "name": "DEFAULT_MODEL",
    "value": "gpt-4o",
    "slotSetting": false
  },
  {
    "name": "AZURE_OPENAI_BASE_URL",
    "value": "https://<YOUR-OPENAI-RESOURCE>.openai.azure.com",
    "slotSetting": false
  },
  {
    "name": "AZURE_USE_MANAGED_IDENTITY",
    "value": "true",
    "slotSetting": false
  },
  {
    "name": "AZURE_CLIENT_ID",
    "value": "<YOUR-MANAGED-IDENTITY-CLIENT-ID>",
    "slotSetting": false
  }
]
```

4. **Replace the placeholder values:**
   - `<YOUR-OPENAI-RESOURCE>` → Your Azure OpenAI resource name
   - `<YOUR-MANAGED-IDENTITY-CLIENT-ID>` → Your managed identity's client ID

**Configuration Options:**

- Set `LLM_PROVIDER=azure` to use Azure OpenAI (default: "openai")
- Set `DEFAULT_MODEL=gpt-4o` to specify the model (default: "gpt-4o")
- For Azure OpenAI, ensure your deployment name matches the `DEFAULT_MODEL` value

**Authentication Options:**

- **Managed Identity (Recommended)**: Set `AZURE_USE_MANAGED_IDENTITY=true`
- **API Key (Fallback)**: If managed identity fails, add `AZURE_OPENAI_API_KEY` and remove `AZURE_USE_MANAGED_IDENTITY`

For API key authentication, add this environment variable instead:

```json
{
  "name": "AZURE_OPENAI_API_KEY",
  "value": "your-azure-openai-api-key",
  "slotSetting": false
}
```

5. Click **"OK"** → **"Save"** → **"Continue"**

### 6. Quick Verification

Before deploying code, verify your App Service is properly configured:

1. Go to **"Overview"** → Click your app URL
2. You should see the Microsoft login (if configured) or a default App Service page
3. Check basic health:
   ```bash
   curl https://<YOUR-APP-NAME>.azurewebsites.net
   ```
   Should return HTML content (login page or default page)

### 7. Deploy Application

1. **Install Azure CLI** (if not already installed)
2. **Sign In:**
   ```bash
   az login
   ```
3. **Deploy directly from folder:**
   ```bash
   cd apps/document-generator
   az webapp up \
      --name <YOUR-APP-NAME> \
      --resource-group <YOUR-RESOURCE-GROUP> \
      --plan <YOUR-APP-SERVICE-PLAN> \
      --runtime "PYTHON|3.11" \
      --sku B1 \
      --logs
   ```

### 8. Verify Deployment

1. Go to **"Overview"** → Click your app URL
2. Document generator should load
3. Test document generation with Azure OpenAI

## Troubleshooting

**Build fails with "No matching distribution found"?**

- Check requirements.txt for local packages not available on PyPI
- Remove any internal/monorepo package references
- Ensure all packages are publicly available

**Files not appearing in /home/site/wwwroot?**

- This is normal for Python apps with build automation - files are actually in `/tmp/zipdeploy/extracted`
- Check logs for build failures preventing deployment
- Verify requirements.txt installs successfully

**App won't start?**

- Check **"Log stream"** in Azure Portal for specific error messages
- Verify startup command is set to `python startup.py`

**Azure OpenAI connection fails?**

- **"App Service managed identity configuration not found in environment. invalid_scope"**:

  - Verify managed identity has **"Cognitive Services OpenAI User"** role on your Azure OpenAI resource
  - Role assignment can take 5-10 minutes to propagate after creation
  - Confirm `AZURE_CLIENT_ID` matches your managed identity's client ID
  - Ensure the managed identity is properly assigned to the App Service

- **General troubleshooting**:
  - Check **"Log stream"** for detailed error messages
  - Verify `AZURE_OPENAI_BASE_URL` format: `https://your-resource.openai.azure.com/`
  - Confirm your Azure OpenAI deployment name matches `DEFAULT_MODEL` value

## Required Files

Essential files for deployment (in order of importance):

1. `startup.py` - App Service entry point
2. `requirements.txt` - Python dependencies
3. `runtime.txt` - Should contain: `python-3.11`
4. `document_generator_app/` - Application code directory

That's it! Your document generator is now live with secure Azure OpenAI access.
