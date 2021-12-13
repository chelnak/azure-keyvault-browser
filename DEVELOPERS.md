# Developing

Welcome to the developer guid for `azure-keyvault-browser`! All commands assume that you are running them from the root of the repository.

## Setting up your environment

```bash
make init
```

This will install dependencies and pre-commit hooks.

Optionally you can use the provided terraform scripts to build a keyvault with some random secret entries inside.

```bash
terraform init
terraform plan
terraform apply
```

### Run the app in dev mode

You can also start an instance of azure-keyvault-browser that is configured to talk to the instance of Key Vault set up by the terraform scripts. This is recommended when developing as it essentially runs the app with the `--debug` switch along with some custom configuration for the local dev environment.

```bash
make app-run
```

## Releasing stuff

Releasing is a semi manual but well oiled method. Tags are used to trigger the release steps in the ci process.

Run the following command. It will tag and push the latest commit triggering a release.

```bash
make tag version="v0.0.5"
```
