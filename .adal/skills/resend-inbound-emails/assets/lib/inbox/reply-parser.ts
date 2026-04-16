/**
 * Reply Content Parser
 * 
 * Strips quoted/forwarded content from email replies to extract
 * only the new reply content.
 */

export interface ParsedReplyContent {
  textBody: string | null;
  htmlBody: string | null;
}

/**
 * Parse reply content by stripping quoted text from both text and HTML versions
 */
export function parseReplyContent(
  text: string | null | undefined,
  html: string | null | undefined
): ParsedReplyContent {
  return {
    textBody: text ? stripQuotedText(text) : null,
    htmlBody: html ? stripQuotedHtml(html) : null,
  };
}

/**
 * Strip quoted text patterns from plain text email
 * Handles common email client quote formats
 */
export function stripQuotedText(text: string): string {
  let result = text;

  // Pattern 1: "On [date], [name] <[email]> wrote:" (Gmail, Apple Mail)
  result = result.replace(
    /\n*On .+? wrote:\s*\n[\s\S]*$/i,
    ""
  );

  // Pattern 2: "-------- Original Message --------" (Outlook)
  result = result.replace(
    /\n*-{3,}\s*Original Message\s*-{3,}[\s\S]*$/i,
    ""
  );

  // Pattern 3: "From: [email]" block (Outlook/forwarded)
  result = result.replace(
    /\n*From:\s*[^\n]+\n(?:Sent|Date):\s*[^\n]+\n(?:To|Subject):\s*[^\n]+[\s\S]*$/i,
    ""
  );

  // Pattern 4: Lines starting with ">" (standard quote prefix)
  const lines = result.split("\n");
  const nonQuotedLines: string[] = [];
  let foundQuoteBlock = false;

  for (const line of lines) {
    // If line starts with >, we're in a quote block
    if (/^>+\s*/.test(line)) {
      foundQuoteBlock = true;
      continue;
    }
    // After finding quotes, skip empty lines that follow
    if (foundQuoteBlock && line.trim() === "") {
      continue;
    }
    // If we hit a non-empty, non-quote line after quotes, we're done with quotes
    if (foundQuoteBlock && line.trim() !== "") {
      foundQuoteBlock = false;
    }
    if (!foundQuoteBlock) {
      nonQuotedLines.push(line);
    }
  }

  result = nonQuotedLines.join("\n").trim();
  return result;
}

/**
 * Strip quoted HTML content from email
 * Handles common email client HTML quote structures
 */
export function stripQuotedHtml(html: string): string {
  let result = html;

  // Gmail quote block: <div class="gmail_quote">...</div>
  result = result.replace(
    /<div[^>]*class="gmail_quote"[^>]*>[\s\S]*?<\/div>/gi,
    ""
  );

  // Outlook quote block: <div id="divRplyFwdMsg">...</div>
  result = result.replace(
    /<div[^>]*id="divRplyFwdMsg"[^>]*>[\s\S]*$/gi,
    ""
  );

  // Generic blockquote elements
  result = result.replace(
    /<blockquote[^>]*>[\s\S]*?<\/blockquote>/gi,
    ""
  );

  // "On ... wrote:" patterns in HTML
  result = result.replace(
    /<div[^>]*>On .+? wrote:<\/div>[\s\S]*$/gi,
    ""
  );

  // Clean up empty divs and multiple line breaks
  result = result.replace(/<div[^>]*>\s*<\/div>/gi, "");
  result = result.replace(/(<br\s*\/?>\s*){3,}/gi, "<br><br>");

  return result.trim();
}
