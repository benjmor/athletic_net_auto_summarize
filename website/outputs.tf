output "api_gateway_url" {
    value = "https://${aws_api_gateway_rest_api.website_api.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${aws_api_gateway_deployment.api_gateway_deployment.stage_name}/submit_meet"
}