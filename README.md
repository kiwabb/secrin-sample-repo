# Secrin Sample Test Repository
This is a target repository for testing the Secrin 'build' command.

## Added Business Sample

This repository now includes a compact commerce workflow used for code analysis tests.

Files:
- `order_models.py`: request, payment, refund, and result models
- `pricing.py`: tier pricing, coupon rules, points redemption, shipping, and tax
- `inventory.py`: stock check and reservation logic
- `risk.py`: blocked country, velocity, high-risk category, and amount rules
- `checkout.py`: end-to-end checkout orchestration and refund decisions
- `demo_scenarios.py`: executable scenarios for sample order and refund flows

The goal is to keep the codebase small, but still include enough cross-module business logic for graph building, code summarization, search, and chat testing.
