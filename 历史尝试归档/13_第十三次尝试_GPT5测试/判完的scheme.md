{
  "properties": {
    // ... 所有现有字段保持不变
    
    "verification": {
      "type": "object",
      "description": "Answer verification results from multiple expert models",
      "required": [
        "status",
        "verifiers",
        "verified_at"
      ],
      "properties": {
        "status": {
          "type": "string",
          "description": "Overall verification status",
          "enum": ["approved", "needs_review", "rejected"]
        },
        "verifiers": {
          "type": "array",
          "description": "Verification results from each model",
          "minItems": 3,
          "items": {
            "type": "object",
            "required": [
              "model_name",
              "correct",
              "baseline_confidence",
              "verification_confidence"
            ],
            "properties": {
              "model_name": {
                "type": "string",
                "description": "Name of the verifying model",
                "examples": ["claude-sonnet-4.5", "gemini-2.5-pro", "gpt-5"]
              },
              "correct": {
                "type": "boolean",
                "description": "Whether the answer is factually correct"
              },
              "baseline_confidence": {
                "type": "string",
                "description": "Confidence without original text",
                "enum": ["high", "medium", "low"]
              },
              "verification_confidence": {
                "type": "string",
                "description": "Confidence in verification judgment",
                "enum": ["high", "medium", "low"]
              },
              "issues": {
                "type": "array",
                "description": "Specific issues found (empty if none)",
                "items": {
                  "type": "string"
                }
              },
              "reasoning": {
                "type": "string",
                "description": "Brief explanation of the judgment"
              }
            }
          }
        },
        "verified_at": {
          "type": "string",
          "description": "Timestamp of verification in ISO 8601 format",
          "format": "date-time"
        },
        "consensus": {
          "type": "object",
          "description": "Summary of verification consensus",
          "properties": {
            "all_correct": {
              "type": "boolean",
              "description": "Whether all verifiers marked as correct"
            },
            "all_high_confidence": {
              "type": "boolean",
              "description": "Whether all verifiers had high verification confidence"
            },
            "disagreement_count": {
              "type": "integer",
              "description": "Number of verifiers who disagreed",
              "minimum": 0
            }
          }
        }
      }
    }
  }
}