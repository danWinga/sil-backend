{{/*
Define si-keycloak.fullname by delegating to the Bitnami subchart helper.
*/}}
{{- define "si-keycloak.fullname" -}}
{{- include "keycloak.fullname" . -}}
{{- end -}}