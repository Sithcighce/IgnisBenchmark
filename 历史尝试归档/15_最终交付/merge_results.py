#!/usr/bin/env python3
"""
Merge temp verification results into pass.json and notpass.json
"""
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

VERIFY_DIR = Path(__file__).parent
TEMP_DIR = VERIFY_DIR / 'verification_output' / 'temp'
PASS_FILE = VERIFY_DIR / 'pass.json'
NOTPASS_FILE = VERIFY_DIR / 'notpass.json'
STATS_FILE = VERIFY_DIR / 'verification_stats.json'

def main():
    print("=" * 80)
    print("MERGING VERIFICATION RESULTS")
    print("=" * 80)
    
    if not TEMP_DIR.exists():
        print(f"❌ Temp directory not found: {TEMP_DIR}")
        return
    
    # Collect all temp files
    temp_files = list(TEMP_DIR.glob("*.json"))
    print(f"Found {len(temp_files)} temp files\n")
    
    pass_items = []
    notpass_items = []
    
    status_counts = defaultdict(int)
    
    for temp_file in temp_files:
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                item = json.load(f)
            
            status = item.get("verification", {}).get("status", "needs_review")
            status_counts[status] += 1
            
            if status == "approved":
                pass_items.append(item)
            else:
                notpass_items.append(item)
                
        except Exception as e:
            print(f"⚠ Error reading {temp_file.name}: {e}")
    
    # Save results
    print(f"\n📊 Results:")
    print(f"  Approved: {len(pass_items)}")
    print(f"  Not Approved: {len(notpass_items)}")
    print(f"    - needs_review: {status_counts['needs_review']}")
    print(f"    - rejected: {status_counts['rejected']}")
    
    if pass_items:
        with open(PASS_FILE, 'w', encoding='utf-8') as f:
            json.dump(pass_items, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Saved {len(pass_items)} approved questions to: {PASS_FILE}")
    
    if notpass_items:
        with open(NOTPASS_FILE, 'w', encoding='utf-8') as f:
            json.dump(notpass_items, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved {len(notpass_items)} not-approved questions to: {NOTPASS_FILE}")
    
    # Generate statistics
    print(f"\n📈 Generating statistics...")
    
    stats = {
        "generation_time": datetime.now().isoformat(),
        "total_questions": len(temp_files),
        "results": {
            "approved": len(pass_items),
            "not_approved": len(notpass_items),
            "approval_rate": f"{len(pass_items)/max(1, len(temp_files))*100:.2f}%"
        },
        "status_breakdown": dict(status_counts)
    }
    
    # Analyze pass.json for more details
    if pass_items:
        # Consensus analysis
        all_correct_count = sum(1 for item in pass_items 
                                if item.get("verification", {}).get("consensus", {}).get("all_correct") is True)
        all_high_conf_count = sum(1 for item in pass_items 
                                  if item.get("verification", {}).get("consensus", {}).get("all_high_confidence") is True)
        
        stats["pass_details"] = {
            "all_models_correct": all_correct_count,
            "all_high_confidence": all_high_conf_count,
            "unanimous_approval_rate": f"{all_correct_count/max(1, len(pass_items))*100:.2f}%"
        }
        
        # Difficulty distribution
        difficulty_dist = defaultdict(int)
        for item in pass_items:
            diff = item.get("difficulty", "unknown")
            difficulty_dist[str(diff)] += 1
        stats["pass_by_difficulty"] = dict(difficulty_dist)
        
        # Topic distribution
        topic_dist = defaultdict(int)
        for item in pass_items:
            topic = item.get("topic", "unknown")
            topic_dist[topic] += 1
        stats["pass_by_topic"] = dict(sorted(topic_dist.items(), key=lambda x: x[1], reverse=True))
        
        # Type distribution
        type_dist = defaultdict(int)
        for item in pass_items:
            qtype = item.get("type", "unknown")
            type_dist[qtype] += 1
        stats["pass_by_type"] = dict(type_dist)
    
    # Analyze notpass.json
    if notpass_items:
        # Count needs_review vs rejected
        needs_review = sum(1 for item in notpass_items 
                          if item.get("verification", {}).get("status") == "needs_review")
        rejected = sum(1 for item in notpass_items 
                      if item.get("verification", {}).get("status") == "rejected")
        
        stats["notpass_details"] = {
            "needs_review": needs_review,
            "rejected": rejected
        }
    
    # Save statistics
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Statistics saved to: {STATS_FILE}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"\n📊 Overall:")
    print(f"   Total Questions: {stats['total_questions']}")
    print(f"   Approved: {stats['results']['approved']} ({stats['results']['approval_rate']})")
    print(f"   Not Approved: {stats['results']['not_approved']}")
    
    if "pass_details" in stats:
        print(f"\n🎯 Pass Quality:")
        print(f"   All Models Agreed: {stats['pass_details']['all_models_correct']}")
        print(f"   All High Confidence: {stats['pass_details']['all_high_confidence']}")
        print(f"   Unanimous Rate: {stats['pass_details']['unanimous_approval_rate']}")
    
    if "notpass_details" in stats:
        print(f"\n⚠️  Not Approved:")
        print(f"   Needs Review: {stats['notpass_details']['needs_review']}")
        print(f"   Rejected: {stats['notpass_details']['rejected']}")
    
    if "pass_by_difficulty" in stats:
        print(f"\n📈 Pass by Difficulty:")
        for diff in sorted(stats['pass_by_difficulty'].keys()):
            count = stats['pass_by_difficulty'][diff]
            print(f"   Level {diff}: {count} questions")
    
    if "pass_by_type" in stats:
        print(f"\n📝 Pass by Type:")
        for qtype, count in sorted(stats['pass_by_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {qtype}: {count} questions")
    
    if "pass_by_topic" in stats:
        print(f"\n📚 Top 10 Topics:")
        for topic, count in list(stats['pass_by_topic'].items())[:10]:
            print(f"   {topic}: {count} questions")
    
    print("\n" + "=" * 80)
    print("✅ MERGE COMPLETE!")
    print("=" * 80)


if __name__ == '__main__':
    main()
