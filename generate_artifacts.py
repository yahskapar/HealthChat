#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reconstructs the specified version of the HealthChat-11K dataset and generates
two review CSVs - one for the entire dataset and one for sycophancy exploration.

Note: This script uses a hardcoded version string to download the corresponding
master annotation file from the Hugging Face Hub. It then generates the final
dataset and all review artifacts for that specific version, saving them into
a dedicated, version-specific output directory.
"""

import json
import csv
import os
from collections import defaultdict
from datasets import load_dataset
from datetime import datetime

# --- Configuration ---
# Accepted versions ["1.0.0"]
DATASET_VERSION = "1.0.0"

# A dedicated output directory for all generated files
OUTPUT_DIR = f'HealthChat-11K_v{DATASET_VERSION}_artifacts'

ANNOTATIONS_FILENAME = f"HealthChat-11K_master_annotations_v{DATASET_VERSION}.jsonl"
OUTPUT_DATASET_PATH = os.path.join(OUTPUT_DIR, f'HealthChat-11K_v{DATASET_VERSION}.jsonl')
OUTPUT_FULL_REVIEW_CSV = os.path.join(OUTPUT_DIR, f'HealthChat-11K_v{DATASET_VERSION}_full_review.csv')
OUTPUT_SYCOPHANCY_REVIEW_CSV = os.path.join(OUTPUT_DIR, f'HealthChat-11K_v{DATASET_VERSION}_sycophancy_review.csv')

# The HF repository ID where the annotations are stored
ANNOTATIONS_REPO_ID = "yahskapar/HealthChat-11K"

# Mapping to find the original source datasets on HF
DATASET_MAPPING = {
    'lmsys': {
        'path': 'lmsys/lmsys-chat-1m',
        'id_field': 'conversation_id'
    },
    'wildchat': {
        'path': 'allenai/WildChat-1M',
        'id_field': 'conversation_hash'
    }
}

# Human-readable mapping for specialties, used in review CSVs.
SPECIALTIES_MAP = {
    1: "General Health", 2: "Mental Health", 3: "Allergy and Immunology",
    4: "Cardiology", 5: "Dermatology", 6: "Endocrinology",
    7: "Gastroenterology", 8: "Hematology/Oncology", 9: "Infectious Disease",
    10: "Nephrology", 11: "Neurology", 12: "Obstetrics and Gynecology (OB/GYN)",
    13: "Ophthalmology", 14: "Fitness/Orthopedics/Sports Medicine",
    15: "Otolaryngology (ENT)", 16: "Pediatrics", 17: "Pulmonology",
    18: "Rheumatology", 19: "Urology", 20: "Dentistry",
    21: "Diet and Nutrition", 22: "Not a Health Conversation"
}

# --- Helper Functions ---

def json_serial_default(o):
    """JSON serializer for objects not serializable by default, like datetimes."""
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


def load_annotations(hf_repo_id: str, data_filename: str) -> (dict, dict):
    """Loads the master annotations file directly from the Hugging Face Hub."""
    print(f"Downloading master annotation file from Hugging Face repo: {hf_repo_id}/{data_filename}")
    annotations_by_id = {}
    target_ids_by_source = defaultdict(set)
    
    try:
        annotation_dataset = load_dataset(hf_repo_id, data_files=data_filename, split="train")
        for annotation_record in annotation_dataset:
            conv_id = annotation_record.get('conversation_id')
            source = annotation_record.get('dataset_source')
            if conv_id and source in DATASET_MAPPING:
                annotations_by_id[conv_id] = annotation_record
                target_ids_by_source[source].add(conv_id)
    except Exception as e:
        print(f"   ERROR: Failed to download or process annotations from Hugging Face.")
        print(f"   Please check that the version exists in the repo: {hf_repo_id}/{data_filename}")
        print(f"   Error details: {e}")
        exit(1)
        
    for source, ids in target_ids_by_source.items():
        print(f"   - Found {len(ids)} target conversations for dataset '{source}'")
    return annotations_by_id, target_ids_by_source


def write_csv(filepath: str, headers: list, rows: list):
    """A helper function to write data to a CSV file."""
    print(f"\n   Writing {len(rows)} rows to {filepath}...")
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"   -> Successfully created {filepath}")
    except IOError as e:
        print(f"  ERROR: Could not write to CSV file {filepath}: {e}")

# --- End of Helper Functions Section ---

def main():
    """Main function to orchestrate the download, merging, and writing process."""
    
    print(f"  Creating output directory: {OUTPUT_DIR}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    annotations_by_id, target_ids_by_source = load_annotations(ANNOTATIONS_REPO_ID, ANNOTATIONS_FILENAME)
    if not annotations_by_id:
        print("  No valid conversations to process were found. Exiting.")
        return

    full_review_rows = []
    sycophancy_review_rows = []
    found_count = 0
    initial_total_count = len(annotations_by_id)
    
    print(f"\n   Reconstructing final dataset at: {OUTPUT_DATASET_PATH} (version {DATASET_VERSION})")
    
    with open(OUTPUT_DATASET_PATH, 'w', encoding='utf-8') as fout:
        for source, source_info in DATASET_MAPPING.items():
            target_ids = target_ids_by_source.get(source)
            if not target_ids: continue

            dataset_path = source_info['path']
            id_field = source_info['id_field']
            
            print(f"\n   Streaming and searching '{dataset_path}' for {len(target_ids)} conversations...")
            ds_iter = load_dataset(dataset_path, split="train", streaming=True)

            for source_record in ds_iter:
                record_id = source_record.get(id_field)
                if record_id in target_ids:
                    final_record = source_record.copy()
                    annotation_data = annotations_by_id[record_id]
                    final_record.update(annotation_data)
                    final_record['dataset_version'] = DATASET_VERSION
                    fout.write(json.dumps(final_record, default=json_serial_default) + "\n")
                    found_count += 1
                    print(f"   -> Merged and saved: {record_id} ({found_count}/{initial_total_count})")
                    
                    conv_id = final_record.get('conversation_id')
                    web_url = final_record.get('web_url', 'N/A')
                    specialty_code = final_record.get('specialty_conversation_classification')
                    specialty_str = SPECIALTIES_MAP.get(specialty_code, "N/A")
                    
                    taxonomy_by_user_turn = {i: "; ".join(sorted(item.get('taxonomy_codes', []))) for i, item in enumerate(final_record.get('taxonomy_messages_classified', []))}
                    user_turn_idx = 0
                    for turn_idx, turn in enumerate(final_record.get('conversation', [])):
                        role, message = turn.get('role'), turn.get('content', '')
                        tax_codes = taxonomy_by_user_turn.get(user_turn_idx, "") if role == 'user' else ""
                        full_review_rows.append([conv_id, web_url, specialty_str, turn_idx, role, message, tax_codes])
                        if role == 'user': user_turn_idx += 1

                    # Check handles cases where the key is missing, the value is None, or the value is an empty list.
                    if final_record.get('leading_question_classifications'):
                        for lq_item in final_record['leading_question_classifications']:
                            if lq_item.get('classification') != 'N':
                                turn_index = lq_item.get('user_message_original_turn_index')
                                user_message = final_record['conversation'][turn_index].get('content') if turn_index < len(final_record['conversation']) else "TEXT NOT FOUND"
                                prior_assistant_message = final_record['conversation'][turn_index - 1].get('content') if turn_index > 0 else ""
                                lq_user_turn_counter, lq_tax_codes = 0, ""
                                for i, t in enumerate(final_record.get('conversation', [])):
                                    if t.get('role') == 'user':
                                        if i == turn_index:
                                            lq_tax_codes = taxonomy_by_user_turn.get(lq_user_turn_counter, "")
                                            break
                                        lq_user_turn_counter += 1
                                
                                sycophancy_review_rows.append([
                                    conv_id, web_url, turn_index, prior_assistant_message, user_message,
                                    lq_tax_codes, lq_item.get('classification')
                                ])
                    
                    target_ids.remove(record_id)
                    if not target_ids:
                        print(f"     All targets for '{source}' found.")
                        break

    print("\n---")
    print("  Primary dataset reconstruction complete!")
    print(f"   - Wrote {found_count} of {initial_total_count} conversations to {OUTPUT_DATASET_PATH}")
    
    write_csv(OUTPUT_FULL_REVIEW_CSV, 
              ["Conversation ID", "Web URL", "Specialty", "Turn Index", "Role", "Message Text", "Taxonomy Codes"], 
              full_review_rows)
              
    write_csv(OUTPUT_SYCOPHANCY_REVIEW_CSV,
              ["Conversation ID", "Web URL", "User Message Original Turn Index", "Prior Assistant Message Text", "User Message Text", "Taxonomy Codes", "LQST Classification"],
              sycophancy_review_rows)

    any_missing = False
    for source, remaining_ids in target_ids_by_source.items():
        if remaining_ids:
            any_missing = True
            print(f"   -   Could not find {len(remaining_ids)} conversations from source '{source}':")
            for missing_id in remaining_ids:
                print(f"     - {missing_id}")
    if not any_missing:
        print("\n   - All requested conversations were found and merged successfully.")


if __name__ == "__main__":
    main()
