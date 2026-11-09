#!/usr/bin/env bash
# Build the Java web application
# Usage: ./scripts/build_java.sh

set -e
echo "=== Building Java Web Application ==="

if ! command -v mvn &>/dev/null; then
    echo "Maven not found. Please install Maven."
    exit 1
fi

cd java-webapp
mvn clean package -DskipTests
echo "Build complete: java-webapp/target/choptyuk-webapp.jar"
echo "Run with: java -jar java-webapp/target/choptyuk-webapp.jar"
