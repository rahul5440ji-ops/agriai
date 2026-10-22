#!/bin/bash
# AgriAI frontend runner
set -e

# Start the Vite development server
npm run dev --prefix frontend

echo "Frontend started on http://localhost:3000"