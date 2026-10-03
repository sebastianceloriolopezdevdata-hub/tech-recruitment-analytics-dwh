from pathlib import Path

import pandas as pd
import great_expectations as gx


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "candidates.csv"
)


# ---------------------------------------------------------
# Load the Candidate Applications dataset
# ---------------------------------------------------------

df = pd.read_csv(
    DATA_PATH,
    sep=";"
)

print("Dataset shape:", df.shape)


# ---------------------------------------------------------
# Create the Great Expectations Data Context
# ---------------------------------------------------------

context = gx.get_context(
    mode="ephemeral"
)

print("GX Data Context created successfully.")
print("Context type:", type(context).__name__)

# ---------------------------------------------------------
# Create the Pandas Data Source
# ---------------------------------------------------------

data_source = context.data_sources.add_pandas(
    name="candidates_pandas_source"
)

print("Pandas Data Source created successfully.")
print("Data Source name:", data_source.name)

# ---------------------------------------------------------
# Create the Data Asset
# ---------------------------------------------------------

data_asset = data_source.add_dataframe_asset(
    name="candidate_applications"
)

print("Data Asset created successfully.")
print("Data Asset name:", data_asset.name)

# ---------------------------------------------------------
# Create the Batch Definition
# ---------------------------------------------------------

batch_definition = data_asset.add_batch_definition_whole_dataframe(
    name="whole_candidates_dataframe"
)

print("Batch Definition created successfully.")
print("Batch Definition name:", batch_definition.name)

# ---------------------------------------------------------
# Create the Batch
# ---------------------------------------------------------

batch_parameters = {
    "dataframe": df
}

batch = batch_definition.get_batch(
    batch_parameters=batch_parameters
)

print("Batch created successfully.")
print("Batch type:", type(batch).__name__)

"""
# ---------------------------------------------------------
# Step 12 — Define and Test the First Expectation
# DQ02 — Code Challenge Score must be between 0 and 10
# ---------------------------------------------------------

score_expectation = gx.expectations.ExpectColumnValuesToBeBetween(
    column="Code Challenge Score",
    min_value=0,
    max_value=10,
    severity="critical",
)

print("Expectation created successfully.")
print(
    "Expectation type:",
    type(score_expectation).__name__,
)

validation_result = batch.validate(
    score_expectation
)

print(
    "Expectation passed:",
    validation_result.success,
)

print(
    "Unexpected count:",
    validation_result.result["unexpected_count"],
)

# ---------------------------------------------------------
# Step 13 — Create the Expectation Suite
# ---------------------------------------------------------

# Create the Expectation Suite
new_suite = gx.ExpectationSuite(
    name="candidate_quality_suite"
)

# Register the Suite in the Data Context
candidate_suite = context.suites.add(
    new_suite
)

print("Expectation Suite created successfully.")
print("Suite name:", candidate_suite.name)

# Add the tested DQ02 Expectation to the Suite

candidate_suite.add_expectation(
    score_expectation
)

print("DQ02 added to the Expectation Suite.")
print(
    "Number of Expectations:",
    len(candidate_suite.expectations),
)

# ---------------------------------------------------------
# Step 14 — Add the Remaining Expectations to the Suite
# ---------------------------------------------------------

# DQ01 — Technology should be present in at least 98% of rows
technology_expectation = gx.expectations.ExpectColumnValuesToNotBeNull(
    column="Technology",
    mostly=0.98,
    severity="warning",
)

candidate_suite.add_expectation(
    technology_expectation
)


# DQ03 — Technical Interview Score must be between 0 and 10
interview_expectation = gx.expectations.ExpectColumnValuesToBeBetween(
    column="Technical Interview Score",
    min_value=0,
    max_value=10,
    severity="critical",
)

candidate_suite.add_expectation(
    interview_expectation
)

print("DQ01 and DQ03 added successfully.")

print(
    "Number of Expectations:",
    len(candidate_suite.expectations),
)

# ---------------------------------------------------------
# Step 15 — Create the Validation Definition
# ---------------------------------------------------------

new_validation_definition = gx.ValidationDefinition(
    name="candidate_validation_definition",
    data=batch_definition,
    suite=candidate_suite,
)

validation_definition = context.validation_definitions.add(
    new_validation_definition
)

print("Validation Definition created successfully.")
print(
    "Validation Definition name:",
    validation_definition.name,
)

# ---------------------------------------------------------
# Step 16 — Run the Validation Definition
# ---------------------------------------------------------

validation_result = validation_definition.run(
    batch_parameters={
        "dataframe": df
    },
    result_format={
        "result_format": "SUMMARY"
    },
)

print("Validation executed successfully.")

print(
    "Overall validation success:",
    validation_result.success,
)

# ---------------------------------------------------------
# Step 17 — Inspect the Validation Results
# ---------------------------------------------------------

print("\nValidation Summary")
print("------------------")
print(
    "Overall success:",
    validation_result.success,
)
print(
    "Expectations evaluated:",
    len(validation_result.results),
)

for result in validation_result.results:
    expectation = result.expectation

    print("\nExpectation:", type(expectation).__name__)
    print("Column:", getattr(expectation, "column", None))
    print("Severity:", expectation.severity)
    print("Success:", result.success)
    print(
        "Unexpected count:",
        result.result.get("unexpected_count", 0),
    )
    print(
        "Unexpected percent:",
        result.result.get("unexpected_percent", 0),
    )


# ---------------------------------------------------------
# Step 18 — Create a controlled failure
# ---------------------------------------------------------

import math

df_bad = df.copy()

# DQ02 failure:
# introduce invalid Code Challenge Score values

df_bad.loc[
    df_bad.index[:100],
    "Code Challenge Score"
] = 15

# DQ01 failure:
# introduce approximately 3% missing Technology values

n_missing_technology = math.ceil(
    len(df_bad) * 0.03
)

technology_idx = (
    df_bad.index[
        df_bad["Technology"].notna()
    ][:n_missing_technology]
)

df_bad.loc[
    technology_idx,
    "Technology"
] = None


bad_validation_result = validation_definition.run(
    batch_parameters={
        "dataframe": df_bad
    },
    result_format={
        "result_format": "SUMMARY"
    },
)

print(
    "Overall validation success:",
    bad_validation_result.success,
)

print("\nControlled Failure Results")
print("--------------------------")

for result in bad_validation_result.results:
    expectation = result.expectation

    print("\nExpectation:", type(expectation).__name__)
    print("Column:", getattr(expectation, "column", None))
    print("Severity:", expectation.severity)
    print("Success:", result.success)
    print(
        "Unexpected count:",
        result.result.get("unexpected_count", 0),
    )
    print(
        "Unexpected percent:",
        result.result.get("unexpected_percent", 0),
    )

# ---------------------------------------------------------
# Step 19 — Interpret Failure Severity
# and Define the Pipeline Response
# ---------------------------------------------------------

failed_results = [
    result
    for result in bad_validation_result.results
    if not result.success
]

print("\nFailed Expectations")
print("-------------------")

for result in failed_results:
    expectation = result.expectation

    print(
        type(expectation).__name__,
        "-",
        getattr(expectation, "column", None),
        "- Severity:",
        expectation.severity,
    )

has_critical_failure = any(
    str(result.expectation.severity).lower().endswith("critical")
    for result in failed_results
)

has_warning_failure = any(
    str(result.expectation.severity).lower().endswith("warning")
    for result in failed_results
)

if has_critical_failure:
    pipeline_action = "STOP"

elif has_warning_failure:
    pipeline_action = "CONTINUE WITH WARNING"

else:
    pipeline_action = "CONTINUE"


print(
    "\nPipeline action:",
    pipeline_action,
)

# ---------------------------------------------------------
# Step 20 — Create and Register the Checkpoint
# ---------------------------------------------------------

new_checkpoint = gx.Checkpoint(
    name="candidate_validation_checkpoint",
    validation_definitions=[
        validation_definition
    ],
    actions=[],
    result_format={
        "result_format": "SUMMARY"
    },
)

checkpoint = context.checkpoints.add(
    new_checkpoint
)

print("Checkpoint created successfully.")
print("Checkpoint name:", checkpoint.name)

# ---------------------------------------------------------
# Step 21 — Run the Checkpoint
# ---------------------------------------------------------

checkpoint_result = checkpoint.run(
    batch_parameters={
        "dataframe": df
    }
)

print("Checkpoint executed successfully.")
print(
    "Checkpoint success:",
    checkpoint_result.success,
)

bad_checkpoint_result = checkpoint.run(
    batch_parameters={
        "dataframe": df_bad
    }
)

print(
    "Controlled failure checkpoint success:",
    bad_checkpoint_result.success,
)

"""