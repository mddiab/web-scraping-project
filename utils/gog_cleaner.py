#!/usr/bin/env python3
"""
Analyze GOG products CSV for uniqueness and data quality
"""
import csv
import sys
from collections import Counter, defaultdict

def analyze_csv(filename):
    products = []
    fieldnames = []
    
    # Read CSV
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        products = list(reader)
    
    total_products = len(products)
    print(f"=" * 80)
    print(f"CSV ANALYSIS REPORT")
    print(f"=" * 80)
    print(f"\nTotal products: {total_products}")
    print(f"Total fields: {len(fieldnames)}")
    
    # Check uniqueness
    print(f"\n{'=' * 80}")
    print("UNIQUENESS CHECK")
    print(f"{'=' * 80}")
    
    # Check product_id uniqueness
    product_ids = [p.get('product_id', '') for p in products]
    product_id_counts = Counter(product_ids)
    duplicate_ids = {pid: count for pid, count in product_id_counts.items() if count > 1}
    
    if duplicate_ids:
        print(f"\n❌ Found {len(duplicate_ids)} duplicate product_ids:")
        for pid, count in list(duplicate_ids.items())[:10]:
            print(f"   - {pid}: appears {count} times")
        if len(duplicate_ids) > 10:
            print(f"   ... and {len(duplicate_ids) - 10} more")
    else:
        print(f"\n✅ All product_ids are unique ({len(set(product_ids))} unique IDs)")
    
    # Check slug uniqueness
    slugs = [p.get('slug', '') for p in products]
    slug_counts = Counter(slugs)
    duplicate_slugs = {slug: count for slug, count in slug_counts.items() if count > 1}
    
    if duplicate_slugs:
        print(f"\n❌ Found {len(duplicate_slugs)} duplicate slugs:")
        for slug, count in list(duplicate_slugs.items())[:10]:
            print(f"   - {slug}: appears {count} times")
        if len(duplicate_slugs) > 10:
            print(f"   ... and {len(duplicate_slugs) - 10} more")
    else:
        print(f"\n✅ All slugs are unique ({len(set(slugs))} unique slugs)")
    
    # Check URL uniqueness
    urls = [p.get('url', '') for p in products]
    url_counts = Counter(urls)
    duplicate_urls = {url: count for url, count in url_counts.items() if count > 1}
    
    if duplicate_urls:
        print(f"\n❌ Found {len(duplicate_urls)} duplicate URLs:")
        for url, count in list(duplicate_urls.items())[:5]:
            print(f"   - {url[:60]}...: appears {count} times")
        if len(duplicate_urls) > 5:
            print(f"   ... and {len(duplicate_urls) - 5} more")
    else:
        print(f"\n✅ All URLs are unique ({len(set(urls))} unique URLs)")
    
    # Check for completely duplicate rows
    rows_as_tuples = [tuple(p.values()) for p in products]
    row_counts = Counter(rows_as_tuples)
    duplicate_rows = {row: count for row, count in row_counts.items() if count > 1}
    
    if duplicate_rows:
        print(f"\n❌ Found {len(duplicate_rows)} completely duplicate rows:")
        for i, (row, count) in enumerate(list(duplicate_rows.items())[:3]):
            print(f"   - Row {i+1}: appears {count} times")
            print(f"     Example: {row[2][:50]}...")
        if len(duplicate_rows) > 3:
            print(f"   ... and {len(duplicate_rows) - 3} more")
    else:
        print(f"\n✅ No completely duplicate rows found")
    
    # Data quality check
    print(f"\n{'=' * 80}")
    print("DATA QUALITY CHECK")
    print(f"{'=' * 80}")
    
    # Check for missing critical fields
    critical_fields = ['product_id', 'slug', 'title', 'url']
    print(f"\nMissing critical fields:")
    for field in critical_fields:
        missing = sum(1 for p in products if not p.get(field) or p.get(field).strip() == '')
        if missing > 0:
            print(f"   ❌ {field}: {missing} missing ({missing/total_products*100:.1f}%)")
        else:
            print(f"   ✅ {field}: all present")
    
    # Check for N/A values
    print(f"\nFields with 'N/A' values:")
    na_counts = {}
    for field in fieldnames:
        na_count = sum(1 for p in products if p.get(field, '').strip() == 'N/A')
        if na_count > 0:
            na_counts[field] = na_count
            percentage = na_count / total_products * 100
            print(f"   - {field}: {na_count} ({percentage:.1f}%)")
    
    # Check price data quality
    print(f"\nPrice data quality:")
    price_fields = ['price_base', 'price_final', 'price_currency', 'discount_percentage']
    for field in price_fields:
        if field == 'price_currency':
            currencies = Counter(p.get(field, '') for p in products)
            print(f"   - {field}: {len(currencies)} different values")
            for curr, count in currencies.most_common(5):
                print(f"     * {curr}: {count} products")
        elif field == 'discount_percentage':
            discounts = [p.get(field, '0') for p in products]
            try:
                discount_nums = [float(d) for d in discounts if d and d != 'N/A']
                if discount_nums:
                    print(f"   - {field}: range {min(discount_nums):.0f}% - {max(discount_nums):.0f}%, avg {sum(discount_nums)/len(discount_nums):.1f}%")
                    discounted = sum(1 for d in discount_nums if d > 0)
                    print(f"     * {discounted} products have discounts")
            except:
                print(f"   - {field}: parsing error")
        else:
            prices = [p.get(field, '') for p in products]
            valid_prices = [p for p in prices if p and p != 'N/A' and p.replace('.', '').replace('-', '').isdigit()]
            if valid_prices:
                try:
                    price_nums = [float(p) for p in valid_prices]
                    print(f"   - {field}: {len(valid_prices)} valid prices, range ${min(price_nums):.2f} - ${max(price_nums):.2f}")
                except:
                    print(f"   - {field}: {len(valid_prices)} valid prices")
            else:
                print(f"   - {field}: no valid prices found")
    
    # Check URL format
    print(f"\nURL format check:")
    valid_urls = sum(1 for p in products if p.get('url', '').startswith('https://www.gog.com'))
    invalid_urls = total_products - valid_urls
    print(f"   - Valid GOG URLs: {valid_urls} ({valid_urls/total_products*100:.1f}%)")
    if invalid_urls > 0:
        print(f"   - Invalid URLs: {invalid_urls}")
        for p in products[:5]:
            url = p.get('url', '')
            if url and not url.startswith('https://www.gog.com'):
                print(f"     Example: {url[:80]}")
    
    # Check cover_image URLs
    print(f"\nCover image check:")
    valid_images = sum(1 for p in products if p.get('cover_image', '').startswith('http'))
    invalid_images = total_products - valid_images - sum(1 for p in products if p.get('cover_image', '').strip() == 'N/A')
    print(f"   - Valid image URLs: {valid_images} ({valid_images/total_products*100:.1f}%)")
    if invalid_images > 0:
        print(f"   - Invalid image URLs: {invalid_images}")
    
    # Check date format
    print(f"\nRelease date check:")
    dates = [p.get('release_date', '') for p in products]
    valid_dates = sum(1 for d in dates if d and d != 'N/A' and len(d) == 10 and d.count('-') == 2)
    print(f"   - Valid dates (YYYY-MM-DD): {valid_dates} ({valid_dates/total_products*100:.1f}%)")
    
    # Check review scores
    print(f"\nReview score check:")
    scores = [p.get('review_score', '') for p in products]
    valid_scores = [s for s in scores if s and s != 'N/A' and s.replace('.', '').isdigit()]
    if valid_scores:
        try:
            score_nums = [float(s) for s in valid_scores]
            print(f"   - Valid scores: {len(valid_scores)} ({len(valid_scores)/total_products*100:.1f}%)")
            print(f"   - Score range: {min(score_nums):.0f} - {max(score_nums):.0f}, avg {sum(score_nums)/len(score_nums):.1f}")
        except:
            print(f"   - Valid scores: {len(valid_scores)}")
    else:
        print(f"   - No valid review scores found")
    
    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    
    issues = []
    if duplicate_ids:
        issues.append(f"{len(duplicate_ids)} duplicate product_ids")
    if duplicate_slugs:
        issues.append(f"{len(duplicate_slugs)} duplicate slugs")
    if duplicate_urls:
        issues.append(f"{len(duplicate_urls)} duplicate URLs")
    if duplicate_rows:
        issues.append(f"{len(duplicate_rows)} duplicate rows")
    
    missing_critical = sum(1 for field in critical_fields 
                          for p in products if not p.get(field) or p.get(field).strip() == '')
    if missing_critical > 0:
        issues.append(f"{missing_critical} missing critical field values")
    
    if issues:
        print(f"\n⚠️  Issues found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print(f"\n✅ No major issues found!")
    
    print(f"\n✅ Total unique products: {len(set(product_ids))}")
    print(f"✅ Data completeness: {((total_products - sum(1 for p in products if not p.get('title') or p.get('title').strip() == '')) / total_products * 100):.1f}%")
    
    return {
        'total': total_products,
        'unique_ids': len(set(product_ids)),
        'duplicate_ids': len(duplicate_ids),
        'duplicate_slugs': len(duplicate_slugs),
        'duplicate_urls': len(duplicate_urls),
        'duplicate_rows': len(duplicate_rows)
    }

if __name__ == "__main__":
    filename = "gog_products.csv"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    try:
        results = analyze_csv(filename)
        sys.exit(0 if results['duplicate_ids'] == 0 and results['duplicate_rows'] == 0 else 1)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
