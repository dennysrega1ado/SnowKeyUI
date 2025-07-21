# Runbook: Rotating Snowflake User Key Pairs with This Tool

## Overview
This runbook describes how to use the RSA 2048 Key Pair Generator Wizard to rotate Snowflake user key pairs, update them in Snowflake, and store the new private key in AWS Secrets Manager.

---

## Prerequisites

- **Snowflake Privileges:**
  - You must be logged in as a Snowflake user with the `SECURITYADMIN` role or another role with permission to alter other users.
  - You must know the target Snowflake username whose key you are rotating.

- **AWS Permissions:**
  - You must know the name of the AWS Secrets Manager secret where the private key is stored.
  - You must have permissions to update (edit) the existing secret in AWS Secrets Manager.

- **Tool Requirements:**
  - Python 3.8+
  - All dependencies installed (see project README for setup instructions).

---

## Step-by-Step Instructions

### 1. Generate a New Key Pair

1. Launch the tool:
   ```bash
   python gui.py
   ```
2. On the first page:
   - The key name is auto-filled (you can change it if desired).
   - Select the output directory if you want to change it (default: `output_keys`).
   - Click **Next**. The tool will generate a new RSA 2048 key pair.

### 2. Prepare the DDL for Snowflake

1. On the "Results" page, in the **DDL** tab:
   - Enter the target Snowflake username (the user whose key you are rotating).
   - The tool generates a formatted SQL statement:
     ```sql
     ALTER USER <user>
         SET RSA_PUBLIC_KEY = '<public_key>'
     ;
     ```
   - Use the **Copy** button to copy the DDL to your clipboard.

2. In the Snowflake web UI or CLI, execute the DDL as a user with sufficient privileges (see prerequisites).

   > **Note:** You must be logged in as a user with permission to alter the target user (e.g., `SECURITYADMIN`).

### 3. Update the Private Key in AWS Secrets Manager

1. Switch to the **Secret** tab.
   - The tool displays a JSON object:
     ```json
     {
       "user": "<user>",
       "private_key_pem": "<private_key>"
     }
     ```
   - Use the **Copy** button to copy the JSON to your clipboard.

2. In AWS Secrets Manager:
   - Locate the secret by name (you must know the correct secret name).
   - Edit the secret and replace the value with the new JSON (or just update the `private_key_pem` field).
   - Save the changes.

   > **Note:** You must have permissions to edit the secret in AWS Secrets Manager.

---

## Troubleshooting

- **Permission Errors in Snowflake:**
  - Ensure you are using a user/role with `ALTER USER` privileges on the target user.

- **AWS Secrets Manager Access Denied:**
  - Verify your IAM user/role has `secretsmanager:UpdateSecret` or similar permissions for the secret.

- **Key Generation Fails:**
  - Ensure the output directory is writable and you have all Python dependencies installed.

---

## Security Notes
- Never share the private key with unauthorized users.
- Always rotate keys using secure, auditable processes.
- Store private keys only in secure secret managers (never in plaintext or source control).

---

## Improvement Opportunities

### Automating Key Rotation with AWS Lambda

To further improve the security and operational efficiency of Snowflake key pair rotation, consider implementing an automated solution using AWS Lambda:

- **Lambda Function for Auto-Rotation:**
  - Develop a Lambda function that periodically generates new RSA key pairs, updates the public key in Snowflake, and stores the new private key in AWS Secrets Manager.
  - The Lambda can be triggered on a schedule (e.g., monthly) or on-demand.
  - This reduces manual intervention and ensures regular key rotation.

- **Special Snowflake User/Role for Rotation:**
  - Create a dedicated Snowflake user and role specifically for key rotation automation.
  - This user/role must have sufficient privileges to alter the `RSA_PUBLIC_KEY` for all target users—including itself.
  - Limit the permissions of this user/role to only what is necessary for key rotation, and monitor its activity for security.

- **AWS Permissions:**
  - The Lambda's execution role must have permissions to update the relevant secrets in AWS Secrets Manager and to connect to Snowflake with the rotation user.

- **Auditing and Alerts:**
  - Implement logging and alerting for all automated key rotation actions to ensure traceability and rapid response to any issues.

By automating the rotation process, you can further reduce the risk of key compromise and ensure compliance with security best practices. 