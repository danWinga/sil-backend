{{/*
Return the full name of this Keycloak release (delegates to subchart helper).
*/}}
{{- define "si-keycloak.fullname" -}}
{{- include "keycloak.fullname" . -}}
{{- end -}}