# TaxAssist-LLMOps: Event-Driven RAG & Semantic Router
A production-grade LLMOps pipeline that automates the ingestion, embedding, and retrieval of tax documents. This architecture leverages Event-Driven Design to ensure that any document uploaded to S3 is processed in real-time, updating a persistent vector store shared across a unified ECS cluster.

## Technical Architecture
The system is built on a serverless event chain that triggers a user-managed Airflow environment running on ECS Fargate.

The Data Ingestion Flow:
* S3 Upload: A user drops a tax PDF into the inbound S3 bucket.
* EventBridge: S3 emits an ObjectCreated event, which is captured by an EventBridge rule.
* Lambda Orchestrator: EventBridge triggers a Lambda function. This function uses the boto3 ECS client to trigger a specific Airflow task/DAG run.
* ECS Fargate: An ECS task (the "Worker") spins up.
    * RDS Integration: Connects to a Postgres RDS instance to manage/log Airflow metadata.
    * S3 Fetch: The worker pulls the specific file from the S3 bucket.
    * Vector Processing: The worker chunks the document and generates embeddings.
* EFS Persistence: The final vector embeddings are saved/updated in a ChromaDB instance living on an Amazon EFS volume, shared by the FastAPI service.

## Tech Stack
* Orchestration: User-Managed Apache Airflow (running on ECS Fargate).
* Serverless Logic: AWS Lambda & Amazon EventBridge.
* Vector Database: ChromaDB (Persistent on EFS).
* Metadata DB: Amazon RDS (PostgreSQL).
* API Layer: FastAPI with SwaggerUI for instant query review.
* CI/CD: GitHub Actions (Automated Docker builds & ECS deployments).

## Security & CI/CD (GitHub Actions)
We use GitHub Actions to manage the lifecycle of our containers. Secrets are never hardcoded; they are managed through GitHub Secrets and AWS Secrets Manager.

### GitHub Secrets & Variables:
* AWS_REGION / ECR_REPO_URI: Used to dynamically tag and push images to the correct regional registry.
* AWS_ROLE_ARN: We use OIDC (OpenID Connect) to allow GitHub Actions to assume a temporary AWS role. This is more secure than using long-lived IAM keys.

### AWS Secrets Manager:
* OpenAI API Key: Sensitive keys for embedding and LLM generation.
* Model Configs: Used by the Semantic Router to pull specific model IDs (e.g., GPT-4o) without code changes.

### Usage & Review
The app is designed for rapid iteration. Once deployed, developers can use the built-in SwaggerUI to review how the semantic router handles queries.
* URL: http://<ECS_PUBLIC_IP>:8000/docs
* Feature: Test the /chat endpoint to see how queries are classified (e.g., routing a greeting to a general response vs. routing a tax question to the RAG pipeline).
* GET /health: Returns system status and current knowledge base size.
* POST /chat: Accepts a user query and returns a routed RAG response.

### LLMOps Highlights
* Event-Driven Ingestion: Eliminated manual DAG triggers; the system responds to data changes instantly.
* User-Managed Airflow: Opted for a custom ECS-based Airflow setup to maintain full control over costs and environment configurations compared to MWAA.
* Unified Compute: Shared EFS volume allows the API and the Airflow workers to access the same vector "brain" without data duplication.
* Persistence is Key: Solved the challenge of sharing a local vector database across multiple containers in ECS using Amazon EFS.
* Semantic Accuracy: Implemented a router to prevent the LLM from attempting RAG on generic greetings, saving tokens and improving latency.
* CI/CD: Automated the deployment pipeline so every git push updates the ECS task definition and restarts the service.