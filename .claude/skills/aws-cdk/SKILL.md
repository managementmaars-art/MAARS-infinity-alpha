---
name: aws-cdk
description: AWS CDK constructs and stacks for Lambda, API Gateway, DynamoDB, IAM, S3, EventBridge, and CI/CD pipelines.
---

# AWS CDK

## Overview

AWS CDK (Cloud Development Kit) lets you define cloud infrastructure using TypeScript, Python, or Go. It synthesizes to CloudFormation and provides higher-level constructs (L2/L3) that encode AWS best practices.

## Installation & Setup

```bash
npm install -g aws-cdk
cdk init app --language typescript

# Python
pip install aws-cdk-lib constructs

# Bootstrap your AWS account (once per account/region)
cdk bootstrap aws://ACCOUNT_ID/us-east-1
```

## Stack Organization

```typescript
// lib/my-app-stack.ts
import * as cdk from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as iam from "aws-cdk-lib/aws-iam";
import * as logs from "aws-cdk-lib/aws-logs";
import { Construct } from "constructs";

interface MyAppStackProps extends cdk.StackProps {
  environment: "dev" | "staging" | "prod";
}

export class MyAppStack extends cdk.Stack {
  public readonly apiUrl: string;

  constructor(scope: Construct, id: string, props: MyAppStackProps) {
    super(scope, id, props);

    const isProd = props.environment === "prod";

    // DynamoDB table
    const table = new dynamodb.Table(this, "DataTable", {
      tableName: `my-app-${props.environment}`,
      partitionKey: { name: "pk", type: dynamodb.AttributeType.STRING },
      sortKey: { name: "sk", type: dynamodb.AttributeType.STRING },
      billingMode: isProd
        ? dynamodb.BillingMode.PROVISIONED
        : dynamodb.BillingMode.PAY_PER_REQUEST,
      readCapacity: isProd ? 10 : undefined,
      writeCapacity: isProd ? 5 : undefined,
      pointInTimeRecovery: isProd,
      removalPolicy: isProd ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
    });

    // GSI for query patterns
    table.addGlobalSecondaryIndex({
      indexName: "gsi1",
      partitionKey: { name: "gsi1pk", type: dynamodb.AttributeType.STRING },
      sortKey: { name: "gsi1sk", type: dynamodb.AttributeType.STRING },
    });

    // S3 bucket for uploads
    const uploadBucket = new s3.Bucket(this, "UploadBucket", {
      bucketName: `my-app-uploads-${this.account}-${props.environment}`,
      versioned: isProd,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      lifecycleRules: [
        {
          transitions: [
            {
              storageClass: s3.StorageClass.INFREQUENT_ACCESS,
              transitionAfter: cdk.Duration.days(90),
            },
          ],
          expiration: isProd ? undefined : cdk.Duration.days(30),
        },
      ],
      cors: [
        {
          allowedMethods: [s3.HttpMethods.PUT, s3.HttpMethods.POST],
          allowedOrigins: ["https://myapp.com"],
          allowedHeaders: ["*"],
          maxAge: 3000,
        },
      ],
      removalPolicy: isProd ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: !isProd,
    });

    // Lambda function
    const apiFunction = new lambda.Function(this, "ApiFunction", {
      functionName: `my-app-api-${props.environment}`,
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: "index.handler",
      code: lambda.Code.fromAsset("lambda/api", {
        bundling: {
          image: lambda.Runtime.NODEJS_20_X.bundlingImage,
          command: ["bash", "-c", "npm ci && npm run build && cp -r dist/* /asset-output/"],
        },
      }),
      environment: {
        TABLE_NAME: table.tableName,
        BUCKET_NAME: uploadBucket.bucketName,
        ENVIRONMENT: props.environment,
        NODE_OPTIONS: "--enable-source-maps",
      },
      memorySize: isProd ? 512 : 256,
      timeout: cdk.Duration.seconds(30),
      reservedConcurrentExecutions: isProd ? 100 : 10,
      tracing: lambda.Tracing.ACTIVE,       // X-Ray tracing
      logRetention: isProd
        ? logs.RetentionDays.ONE_MONTH
        : logs.RetentionDays.ONE_WEEK,
      layers: [
        lambda.LayerVersion.fromLayerVersionArn(
          this,
          "PowertoolsLayer",
          `arn:aws:lambda:${this.region}:094274105915:layer:AWSLambdaPowertoolsTypeScriptV2:21`
        ),
      ],
    });

    // Grant permissions
    table.grantReadWriteData(apiFunction);
    uploadBucket.grantReadWrite(apiFunction);

    // API Gateway
    const api = new apigateway.RestApi(this, "RestApi", {
      restApiName: `my-app-${props.environment}`,
      description: "My App REST API",
      deployOptions: {
        stageName: props.environment,
        metricsEnabled: true,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        tracingEnabled: true,
        throttlingRateLimit: isProd ? 100 : 10,
        throttlingBurstLimit: isProd ? 200 : 20,
      },
      defaultCorsPreflightOptions: {
        allowOrigins: isProd ? ["https://myapp.com"] : apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
    });

    const integration = new apigateway.LambdaIntegration(apiFunction, {
      proxy: true,
    });

    // API routes
    const v1 = api.root.addResource("v1");
    const users = v1.addResource("users");
    users.addMethod("GET", integration, { authorizationType: apigateway.AuthorizationType.IAM });
    users.addMethod("POST", integration);

    const user = users.addResource("{id}");
    user.addMethod("GET", integration);
    user.addMethod("PUT", integration);
    user.addMethod("DELETE", integration);

    this.apiUrl = api.url;

    // Outputs
    new cdk.CfnOutput(this, "ApiUrl", { value: api.url });
    new cdk.CfnOutput(this, "TableName", { value: table.tableName });
  }
}
```

## Custom Constructs (L3)

```typescript
// lib/constructs/secure-lambda.ts
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as iam from "aws-cdk-lib/aws-iam";
import * as logs from "aws-cdk-lib/aws-logs";
import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";

export interface SecureLambdaProps {
  functionName: string;
  code: lambda.Code;
  handler: string;
  environment?: Record<string, string>;
  timeout?: cdk.Duration;
  memorySize?: number;
}

export class SecureLambda extends Construct {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: SecureLambdaProps) {
    super(scope, id);

    // Dedicated execution role with least privilege
    const role = new iam.Role(this, "ExecutionRole", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AWSLambdaBasicExecutionRole"),
        iam.ManagedPolicy.fromAwsManagedPolicyName("AWSXRayDaemonWriteAccess"),
      ],
    });

    this.function = new lambda.Function(this, "Function", {
      functionName: props.functionName,
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: props.handler,
      code: props.code,
      role,
      environment: {
        ...props.environment,
        LOG_LEVEL: "INFO",
        POWERTOOLS_SERVICE_NAME: props.functionName,
      },
      timeout: props.timeout ?? cdk.Duration.seconds(30),
      memorySize: props.memorySize ?? 256,
      tracing: lambda.Tracing.ACTIVE,
      architecture: lambda.Architecture.ARM_64,  // Graviton2 (cheaper, faster)
      logRetention: logs.RetentionDays.ONE_MONTH,
    });
  }
}
```

## EventBridge & Event-Driven Architecture

```typescript
import * as events from "aws-cdk-lib/aws-events";
import * as targets from "aws-cdk-lib/aws-events-targets";
import * as sqs from "aws-cdk-lib/aws-sqs";

// Event bus
const eventBus = new events.EventBus(this, "AppEventBus", {
  eventBusName: `my-app-${props.environment}`,
});

// Dead letter queue
const dlq = new sqs.Queue(this, "DLQ", {
  retentionPeriod: cdk.Duration.days(14),
});

// Rule: route order events to processor Lambda
new events.Rule(this, "OrderCreatedRule", {
  eventBus,
  eventPattern: {
    source: ["my-app.orders"],
    detailType: ["OrderCreated"],
  },
  targets: [
    new targets.LambdaFunction(orderProcessorFn, {
      deadLetterQueue: dlq,
      maxEventAge: cdk.Duration.hours(2),
      retryAttempts: 3,
    }),
  ],
});

// Scheduled rule (cron)
new events.Rule(this, "DailyDigestRule", {
  schedule: events.Schedule.cron({ minute: "0", hour: "9" }),
  targets: [new targets.LambdaFunction(digestFn)],
});
```

## CDK Pipelines (CI/CD)

```typescript
// lib/pipeline-stack.ts
import * as pipelines from "aws-cdk-lib/pipelines";
import * as codecommit from "aws-cdk-lib/aws-codecommit";

export class PipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const pipeline = new pipelines.CodePipeline(this, "Pipeline", {
      pipelineName: "my-app-pipeline",
      synth: new pipelines.ShellStep("Synth", {
        input: pipelines.CodePipelineSource.gitHub("myorg/my-app", "main", {
          authentication: cdk.SecretValue.secretsManager("github-token"),
        }),
        commands: [
          "npm ci",
          "npm run build",
          "npm test",
          "npx cdk synth",
        ],
      }),
      dockerEnabledForSynth: true,
      crossAccountKeys: true,
    });

    // Dev stage
    const devStage = pipeline.addStage(
      new MyAppStage(this, "Dev", { environment: "dev" }),
    );

    devStage.addPost(
      new pipelines.ShellStep("IntegrationTests", {
        commands: ["npm run test:integration"],
        envFromCfnOutputs: {
          API_URL: devStage.stacks[0].apiUrlOutput,
        },
      })
    );

    // Prod stage with manual approval
    pipeline.addStage(
      new MyAppStage(this, "Prod", { environment: "prod" }),
      {
        pre: [new pipelines.ManualApprovalStep("PromoteToProd")],
      }
    );
  }
}

class MyAppStage extends cdk.Stage {
  public readonly apiUrlOutput: cdk.CfnOutput;

  constructor(scope: Construct, id: string, props: { environment: "dev" | "prod" } & cdk.StageProps) {
    super(scope, id, props);

    const stack = new MyAppStack(this, "MyApp", {
      environment: props.environment,
    });

    this.apiUrlOutput = new cdk.CfnOutput(stack, "ApiUrl", { value: stack.apiUrl });
  }
}
```

## IAM Best Practices

```typescript
// Least-privilege IAM policy
const processingRole = new iam.Role(this, "ProcessingRole", {
  assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
});

// Only allow specific DynamoDB actions on specific table
processingRole.addToPolicy(new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  actions: [
    "dynamodb:GetItem",
    "dynamodb:PutItem",
    "dynamodb:UpdateItem",
    "dynamodb:Query",
  ],
  resources: [
    table.tableArn,
    `${table.tableArn}/index/*`,
  ],
}));

// Secrets Manager access
const secret = secretsmanager.Secret.fromSecretNameV2(this, "DBSecret", "my-app/db");
secret.grantRead(processingRole);

// KMS key for encryption
const key = new kms.Key(this, "AppKey", {
  enableKeyRotation: true,
  alias: `my-app-${props.environment}`,
});
key.grantEncryptDecrypt(processingRole);
```

## CDK CLI Commands

```bash
# Synthesize CloudFormation
cdk synth

# Deploy specific stack
cdk deploy MyAppStack-prod --require-approval never

# Deploy all stacks
cdk deploy --all

# Show diff before deploy
cdk diff

# Destroy (careful in prod!)
cdk destroy MyAppStack-dev

# Check for security issues
cdk synth | cfn_nag_scan --input-path /dev/stdin

# List stacks
cdk list
```

## Key Patterns

- **L2 constructs** have sensible defaults — prefer them over L1 (CfnXxx)
- **Custom L3 constructs** encapsulate patterns — reuse across teams and projects
- **`removalPolicy: RETAIN`** for stateful resources (DDB, S3) in production
- **ARM_64 architecture** for Lambda is 20% cheaper and often faster
- **CDK Pipelines** handle multi-stage, multi-account deployments with built-in promotion gates
- **`cdk diff`** before every deploy in CI — catch unintended changes

## Models to Use

- **claude-opus-4-5**: Multi-account architecture, complex permission boundaries, CDK pipeline design
- **claude-sonnet-4-5**: Stack implementation, custom constructs, EventBridge patterns
- **claude-haiku-3-5**: Simple resource additions, environment variable updates, output definitions
