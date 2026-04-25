#!/bin/bash
# Move corrected mappings to final/, send contam/duplicates to discard/

# raw_*.mp4 → correct names in final/
mv raw/raw_011421.mp4 final/clip-01-jamal-pain.mp4
mv raw/raw_012132.mp4 final/clip-02b-aisha-pain.mp4
mv raw/raw_012255.mp4 final/clip-03-question-hook.mp4
mv raw/raw_012359.mp4 final/clip-25-jamal-first-sale.mp4
mv raw/raw_012417.mp4 final/clip-26-david-inbox-flood.mp4
mv raw/raw_012519.mp4 final/clip-32-aisha-orders-flooding.mp4
mv raw/raw_012757.mp4 final/clip-24-cta-button.mp4
mv raw/raw_013132.mp4 final/clip-08-social-auto-post.mp4
mv raw/raw_013420.mp4 final/clip-15-commander-orchestrating.mp4

# Currently misnamed clips → correct names in final/
mv clip-01-jamal-pain.mp4 final/clip-02-david-pain.mp4
mv clip-02-david-pain.mp4 final/clip-27-david-empty-office.mp4
mv clip-02b-aisha-pain.mp4 final/clip-33-aisha-wholesale-deal.mp4
mv clip-03-question-hook.mp4 final/clip-05-signup-arrow.mp4
mv clip-04-landing-reveal.mp4 final/clip-04-landing-reveal.mp4
mv clip-05-signup-arrow.mp4 final/clip-21-david-family-lunch.mp4
mv clip-06-dashboard-reveal.mp4 final/clip-06-dashboard-reveal.mp4
mv clip-07-content-gen-firing.mp4 final/clip-36-projection-studio.mp4
mv clip-21-david-family-lunch.mp4 final/clip-07-content-gen-firing.mp4
mv clip-21b-aisha-scaled.mp4 final/clip-09-geo-boost.mp4
mv clip-22-three-lives-converge.mp4 final/clip-10-cold-email.mp4
mv clip-23-logo-reveal.mp4 final/clip-11-cold-call.mp4
mv clip-24-cta-button.mp4 final/clip-12-boost-promote.mp4
mv clip-25-jamal-first-sale.mp4 final/clip-28-jamal-momentum.mp4
mv clip-26-david-inbox-flood.mp4 final/clip-22-three-lives-converge.mp4
mv clip-27-david-empty-office.mp4 final/clip-23-logo-reveal.mp4
mv clip-29-maars-builds-jamals-business.mp4 final/clip-16-activity-monitor.mp4
mv clip-31-maars-builds-aishas-business.mp4 final/clip-19-wallet-credits.mp4
mv clip-32-aisha-orders-flooding.mp4 final/clip-13-campaigns.mp4
mv clip-33-aisha-wholesale-deal.mp4 final/clip-17-smart-routing.mp4

# Contaminated/duplicate Aisha pain (clean version) - this is mislabeled "contam" but actually clean Aisha
# Already have clip-02b-aisha-pain from raw_012132, so keep this as alternate
mv tmp/contam-02b-reroll-1.mp4 final/clip-02b-aisha-pain-alt.mp4

# Discard items: contaminated misrenders & duplicates we don't need
mv raw/raw_012234.mp4 discard/maybe-contam-aisha-2.mp4
mv raw/raw_012329.mp4 discard/dup-signup-arrow.mp4
mv raw/raw_012926.mp4 discard/dup-landing-reveal.mp4
mv raw/raw_013543.mp4 discard/contam-451-misrender.mp4
mv clip-20-jamal-brand-launched.mp4 discard/dup-landing-reveal-2.mp4
mv clip-28-jamal-momentum.mp4 discard/dup-dashboard-reveal-2.mp4
mv clip-30-maars-rebuilds-davids-business.mp4 discard/dup-signup-arrow-3.mp4

echo "=== FINAL DIRECTORY ==="
ls final/ | sort
echo ""
echo "=== COUNT ==="
ls final/*.mp4 | wc -l
echo ""
echo "=== MISSING CLIPS ==="
echo "Required clips per brief: 36"
echo "Need to re-fire: 14, 18, 20, 29, 30, 31"
