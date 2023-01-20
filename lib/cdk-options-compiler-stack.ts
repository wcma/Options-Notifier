import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';

export class CdkOptionsCompilerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

  const function_name = "options-compiler"
  const lambda_path = "src/lambda"

  const lambda_handler = new lambda.Function(this, function_name, {
    functionName: function_name,
    runtime: lambda.Runtime.PYTHON_3_8,
    code: lambda.Code.fromAsset(lambda_path),
    handler: "options_compiler.compiler"
    });

  const layer_arn = lambda.LayerVersion.fromLayerVersionArn(this, "yfinance-dev-layer", "arn:aws:lambda:us-east-1:796779436369:layer:yfinance-dev-layer:3");
  lambda_handler.addLayers(layer_arn);

  }
}
