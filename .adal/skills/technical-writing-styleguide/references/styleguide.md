# Technical Writing Styleguide

These are the style conventions we use to produce content that is clear, consistent, and accessible.

## Goals and principles

Our goal is always to **teach**. This often means helping our readers understand complicated technology, either conceptually or by example. Give your reader the exact information they need and include opportunities for them to learn more.

To achieve our goal, our content is:

* **Clear.** Be sure you know what you're writing about. Keep words and sentences as simple as possible.
* **Useful.** Does the content deliver on the promise your headline made? Have you provided all the information the reader will need?
* **Friendly.** Don't underestimate or patronize your reader. Use informal language.

## Voice and tone

Voice and tone is not about what we say, but how we say it. We aim to be consistent, functional and clear. Here are some tips for how to achieve this:

### Point of view

Default to **first person plural** to include the reader in your "team". This means you and the reader are doing something together:

* "Next, we'll install the widget factory to create widgets efficiently."

Sometimes it's more efficient to use the **second person imperative** and "instruct" the reader by telling them what needs to be done. This can be harsher but it's often less wordy, so use your judgement:

* "We can do this by using our package manager. Type `sudo apt install widget-factory`"

When using the imperative, there's no need to say "Please" to the reader.

It's ok to refer to the reader as 'you' in some cases, where the writer is clearly not involved, but in general, default to the 'we' voice wherever possible.

### Voice

Default to **active voice**. This isn't a hard-and-fast rule. Active voice often makes it clearer who is doing what and sounds less stuffy. That said, sometimes passive is simply cleaner (often in cases where there isn't a specific subject) - use your judgement.

### Things to avoid

#### Avoid giving the reader too many options

Often, there are many ways to achieve the same task. Avoid giving the reader options wherever possible - the reader is looking to you for guidance, so be **opinionated** instead of **comprehensive**.

#### Avoid getting in the reader's way:

* "I wrote this guide after encountering difficulties with the software myself"
* "Next, I'm going to show you how to install a widget factory"

#### Avoid 'marketing' speak.

Never try to sell something to the reader. Don't say a product makes things easy, that a design is beautiful, or use any text that you might find on a SaaS landing page.

#### Avoid anything you might find in an encyclopaedia or academic paper.

Your reader isn't interested in definitions - or if they are, they can easily find these elsewhere.

If you're writing an article on NER, instead of starting with

* "Named Entity Recognition (NER) is the task of categorising key words in a text as specific entities."

Consider something more like

* "If you're analyzing a large amount of text, it's often useful to extract named entities from this - identifying people, places, dates and other entities."

#### Avoid assuming knowledge.

This can be tricky because, of course, you always have to assume _some_ level of knowledge when writing technical content. However, we try to avoid assumptions about our reader's skill level.

* "Referring back to the server code, you may notice it requires both a success.html and a cancel.html."

#### Avoid guessing out loud what the reader wants.

It's tempting to start an article with "Are you are a foo who likes to bar but sometimes finds baz?", but this approach defines a narrow audience and you risk alienating anyone who is not a part of it.

#### Avoid giving extraneous context.

It's tempting to give the reader related context or information, but your reader is here to achieve a specific goal. Leave out anything that doesn't help them achieve it.

#### Avoid telling the reader that something is obvious or easy.

This discourages the reader who doesn't find it obvious or easy, and adds no value to the reader who does. You can usually remove the offending words and the sentence keeps its meaning.

#### Avoid relying on formatting for emphasis

It's occasionally useful to use **bold** to draw the reader's attention to something, but this should be done very sparingly, and never for whole phrases or sentences at a time. Generally use **bold** or _italics_, but never mix them in the same document, unless there is a well-defined convention of when to use which.

Never use underlining, unless there is a well-defined existing convention about what it means in a specific context.

## Structure

The structure of your article helps to present information in the clearest way.

### Keep structures as flat as possible.

Use heading 1 (`#` in Markdown) for the title and heading 2 (`##`) to break things down into logical sections. Heading 3 (`###`) can be used where necessary for sub-sections, but in general, having a deeply nested structure makes things harder to follow, harder to edit, and harder to reuse.

### Make headings good for humans and robots

Headings serve multiple functions:

* Are often presented as an outline or table of contents of the article
* Are used heavily by search engines and agents to find relevant content
* Help a reader figure out what is in a specific section and orient themselves

#### Optimizing headings for SEO

In general, longer headings are better for SEO. Including the product/tool name in headings helps people find content from search engines even if it creates some repetition.

#### Using headings as a sales pitch for the article

Many platforms present the headings as a sidebar or at the start of the article. Headings should be compelling and informative, not generic like "Introduction", "Prerequisites", "Setting up".

### Always have content between headings

Don't have a subheading immediately below a heading without any text in between. Add a short sentence to introduce the section, or restructure to use fewer headings.

### Don't switch from explanation to instruction in a way that the reader might overlook

A tutorial often combines _explanation_ and _instruction_. Keep in mind that the reader might be skimming explanation steps. If you suddenly change from explanation to instruction, the reader might accidentally skip the instructions too. Use subheadings to separate instructions from explanations.

### Avoid long paragraphs with many separate steps

Use numbered bullet points for multi-step instructions so the reader can track their place when alt-tabbing between the tutorial and other applications.

### Avoid nested bullets.

Don't nest bullets into several levels. Restructure the content so that you can use separate bullet lists.

### Link as much context as is useful.

Make it clear to the reader what is being linked to. Avoid using extra generic text like `[click here]` when linking.

### Include user-friendly code samples.

Tell the reader exactly _what_ code needs to go _where_, and make it easy to repeat what we are doing. Avoid screenshots of code, and rather present code samples in text, between backtick gates with a language description.

### Avoid long code snippets.

Instead of giving an entire file to copy-paste, break down the code into several steps if possible.

### Annotate screenshots and use context.

* Use contextual screenshots to help readers navigate whichever platform you are directing them to.
* Use a screenshot to demonstrate what your reader should be seeing if they correctly followed your instructions.
* Make use of [1], [2], [3] annotations if several things need to be shown from a single shot.
* Preferably take screenshots using a 4k/retina screen.

### Prefer code blocks to inline code.

It's ok to use markdown's single back-tick syntax to highlight a single word like "Notice the `for` statement below". For any code samples, even if only one line, rather use three backticks and have the code on its own line and in its own section.

Always specify the language after the three backticks where appropriate. You can leave this blank for shell commands.

## Formatting Generative AI examples

When giving a long prompt, put it between backticks as a code block.

If giving examples of chatbot output, use the same.
