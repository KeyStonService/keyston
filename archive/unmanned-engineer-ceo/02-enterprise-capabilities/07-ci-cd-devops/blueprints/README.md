# Pipeline Blueprints

## Service Template
<<<<<<< HEAD
<<<<<<< HEAD

1. Install deps (`npm install -w <service>` /
   `pip install -r requirements.txt`).
=======
1. Install deps (`npm install -w <service>` / `pip install -r requirements.txt`).
>>>>>>> origin/alert-autofix-37
=======

1. Install deps (`npm install -w <service>` / `pip install -r requirements.txt`).
>>>>>>> origin/copilot/sub-pr-402
2. Run lint/test/build。
3. Build container + cosign sign。
4. Deploy via GH Actions → infrastructure/kubernetes。

## Agent Template

- Build Rust/Go binary
- Generate SBOM (syft)
- Sign provenance (core/slsa_provenance)

## Infra Template

- Terraform fmt + validate
- Plan & store artifact
- Apply with approvals
