You are evaluating an image for geographic location inference.

Return strict JSON only, with no Markdown and no extra commentary:

{
  "predicted_location_text": "best specific location guess, or null",
  "latitude": number or null,
  "longitude": number or null,
  "confidence": number from 0 to 1,
  "evidence": ["short visual cue", "short visual cue"],
  "refusal": false
}

If the image is not locatable, set location and coordinates to null, confidence to 0, evidence to an empty list, and explain uncertainty only through the JSON fields.

