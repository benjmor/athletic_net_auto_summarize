output "api_gateway_url" {
    value = "https://${aws_api_gateway_rest_api.website_api.id}.execute-api.${data.aws_region.current}.amazonaws.com/${aws_api_gateway_stage.api_stage.stage_name}/submit_meet"
}