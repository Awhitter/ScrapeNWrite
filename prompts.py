def generate_prompt(task, urls, text_content, audience, topic, timeframe, emphasis_areas, spider_graph_results):
    base_prompt = f"""
As a highly skilled AI content analyst and creator, your task is to {task.lower()} based on the following information:

Spider Graph Analysis:
{spider_graph_results}

URLs: {urls}
Text Content: {text_content}
Target Audience: {audience}
Topic: {topic}
Timeframe: {timeframe}
Areas of Emphasis: {', '.join(emphasis_areas)}

Please consider the Spider Graph analysis results and the specified areas of emphasis when creating your response. Your output should be detailed, specific, and comprehensive, building upon the provided information and any previous analyses.
"""

    task_specific_prompts = {
        "Tone and Style Analysis": """
Conduct an in-depth tone and style analysis of the content, focusing on:
1. Overall tone (e.g., formal, casual, optimistic, critical) - Provide specific examples and explain why this tone is used.
2. Writing style characteristics - Analyze sentence structure, vocabulary complexity, and use of literary devices. Provide examples for each.
3. Rhetorical devices and literary techniques - Identify and explain the effect of at least 5 different techniques used in the content.
4. Alignment with target audience - Evaluate how well the tone and style match the intended audience. Suggest improvements if necessary.
5. Emotional appeal - Analyze how the content evokes emotions in the reader. Provide specific examples.
6. Consistency - Evaluate the consistency of tone and style throughout the content. Highlight any notable shifts or variations.
7. Comparative analysis - Compare the tone and style to similar content in the same field or genre.

For each point, provide detailed explanations and multiple specific examples from the content to support your analysis. Consider how these elements work together to create the overall impact of the content.
""",
        "Write a Factual Wikipedia-like Paper": f"""
Create a comprehensive, well-structured, and factual paper in the style of a Wikipedia article about {topic}. Your paper should:

1. Introduction:
   - Begin with a clear, concise introduction that defines the topic and its significance.
   - Provide a brief overview of the main sections of the article.

2. Historical Context:
   - Discuss the origins and development of {topic} over time.
   - Highlight key milestones and influential figures in its history.

3. Main Concepts and Principles:
   - Explain the fundamental concepts and principles related to {topic}.
   - Use subsections to organize different aspects or subcategories of the topic.

4. Applications and Real-world Examples:
   - Describe how {topic} is applied in various fields or industries.
   - Provide specific case studies or examples to illustrate its practical use.

5. Current State and Future Trends:
   - Analyze the current state of {topic} and its role in contemporary society.
   - Discuss potential future developments and emerging trends.

6. Controversies or Debates:
   - Present any significant controversies, debates, or criticisms surrounding {topic}.
   - Provide balanced viewpoints and cite relevant sources.

7. Impact and Significance:
   - Evaluate the broader impact of {topic} on society, industry, or relevant fields.
   - Discuss its potential long-term implications.

8. See Also:
   - Include a list of related topics or articles for further reading.

9. References:
   - Provide a comprehensive list of citations and references used throughout the article.

Throughout the paper:
- Use a neutral, objective tone appropriate for a Wikipedia article.
- Incorporate relevant statistics, data, and factual information from the provided content and Spider Graph analysis.
- Ensure all claims are supported by reliable sources (use placeholder citations if needed).
- Use appropriate headings and subheadings to organize the content logically.
- Consider the target audience ({audience}) and adjust the complexity of explanations accordingly.
- Take into account the specified timeframe ({timeframe}) when discussing historical context and future trends.

Your goal is to create a comprehensive, authoritative, and well-organized article that serves as a definitive resource on {topic}.
""",
        "Write Tweets from Content": f"""
Create a series of 10 engaging and informative tweets based on the content and analysis provided. Each tweet should:

1. Be concise and within the 280-character limit.
2. Capture a key point, interesting fact, or insight from the content.
3. Use appropriate hashtags related to {topic} and current trends.
4. Be tailored to engage the target audience ({audience}).
5. Consider the specified timeframe ({timeframe}) if relevant.
6. Include a mix of the following types of tweets:
   - Fact-based tweets with surprising or lesser-known information
   - Question-based tweets to encourage engagement
   - Quote tweets featuring key statements from the content
   - Data visualization tweets (describe the type of visual that would accompany the tweet)
   - Call-to-action tweets that encourage further exploration of the topic

For each tweet:
- Provide the tweet text (including hashtags and any mentions).
- Explain the rationale behind the tweet, including its purpose and target audience.
- Suggest the best time to post the tweet based on the content and audience.
- Propose ideas for visual elements that could accompany the tweet (e.g., images, GIFs, or short video concepts).

Additionally:
- Ensure the tweets work together as a cohesive series, telling a broader story about {topic}.
- Vary the style and focus of the tweets to maintain interest and appeal to different segments of your audience.
- Incorporate key insights from the Spider Graph analysis to make the tweets more impactful and data-driven.
- Consider how the tweets could be part of a larger social media campaign or content strategy.

Your goal is to create a diverse and engaging set of tweets that effectively communicates the key points of the content while encouraging audience interaction and further exploration of {topic}.
""",
        "Write a Blog Post Outline": f"""
Create a detailed and comprehensive blog post outline on {topic} for {audience}. Your outline should include:

1. Attention-Grabbing Headline:
   - Provide 3 options for headlines, each with a different approach (e.g., question-based, numbered list, how-to).
   - Explain the rationale behind each headline option.

2. Introduction:
   - Hook: Describe an engaging opening sentence or anecdote to capture the reader's attention.
   - Context: Outline key background information on {topic} to be covered.
   - Thesis: State the main argument or purpose of the blog post.
   - Preview: List the main points to be discussed in the body of the post.

3. Body (at least 5 main sections with subsections):
   For each main section:
   - Provide a clear subheading.
   - List 3-5 key points to be covered.
   - Suggest relevant examples, case studies, or data to support each point.
   - Identify opportunities for internal and external links.
   - Propose ideas for visual elements (e.g., images, infographics, videos) to enhance the section.

4. Practical Application:
   - Outline a section that shows readers how to apply the information in their own lives or work.
   - Include step-by-step instructions or actionable tips.

5. Expert Insights:
   - Suggest places to incorporate quotes or insights from industry experts or thought leaders.
   - Explain how these insights will add credibility and depth to the post.

6. Addressing Counterarguments:
   - Identify potential objections or alternative viewpoints to be addressed.
   - Outline how to tactfully present and respond to these counterarguments.

7. Conclusion:
   - Summarize the key takeaways from the blog post.
   - Reinforce the main thesis or argument.
   - Provide a thought-provoking final statement or call-to-action.

8. Call-to-Action (CTA):
   - Propose 2-3 different CTAs that align with the blog post's goals and audience needs.
   - Explain the reasoning behind each CTA option.

9. Meta Description:
   - Craft a compelling meta description for SEO purposes (under 160 characters).

10. Keywords:
    - List primary and secondary keywords to be naturally incorporated throughout the post.

11. Internal and External Link Strategy:
    - Suggest relevant internal links to other content on the website.
    - Propose high-quality external links to authoritative sources that support the content.

12. Content Upgrades:
    - Recommend ideas for downloadable content upgrades that would add value for readers (e.g., checklists, templates, or guides).

For each section of the outline:
- Provide 2-3 bullet points summarizing the key information to be included.
- Suggest relevant data points or statistics from the Spider Graph analysis to incorporate.
- Consider the specified timeframe ({timeframe}) and how it affects the content's relevance or approach.
- Ensure that the outline addresses all relevant areas of emphasis: {', '.join(emphasis_areas)}.

Your goal is to create a comprehensive and well-structured outline that will guide the creation of an engaging, informative, and valuable blog post for the target audience ({audience}) on {topic}.
""",
        "Turn Content into a Listicle": f"""
Transform the provided content into an engaging and comprehensive listicle format for {audience} on the topic of {topic}. Your listicle should:

1. Title:
   - Create an attention-grabbing title that includes a number (e.g., "15 Surprising Facts About...")
   - Provide 3 title options and explain the rationale behind each

2. Introduction:
   - Write a brief, engaging introduction (2-3 paragraphs) that:
     a) Explains the relevance of {topic} to the target audience
     b) Sets expectations for what readers will learn
     c) Includes a compelling statistic or fact from the Spider Graph analysis

3. List Items (create at least 15 items):
   For each list item:
   - Write a concise, intriguing subheading
   - Provide a detailed paragraph (100-150 words) expanding on the point
   - Include a relevant example, case study, or data point to support the information
   - Suggest a visual element (e.g., image, infographic, or gif) to accompany the item
   - Incorporate SEO-friendly keywords naturally

4. Varied Content Types:
   Ensure your list includes a mix of the following:
   - Factual information derived from the provided content
   - Expert opinions or quotes (use placeholder quotes if necessary)
   - Statistical data or research findings
   - Practical tips or actionable advice
   - Common misconceptions or myths debunked
   - Future trends or predictions related to {topic}

5. Audience Engagement:
   - For at least 5 list items, include a "Pro Tip" or "Quick Action" box with additional, actionable information
   - Create 2-3 "Did You Know?" boxes with surprising facts to maintain reader interest
   - Suggest places to insert poll or quiz elements to increase interactivity

6. Internal Structure:
   - Group related list items together under broader categories
   - Use transitional phrases between groups to maintain flow and coherence

7. Conclusion:
   - Summarize the key takeaways from the listicle
   - Provide a forward-looking statement about the future of {topic}
   - Include a strong call-to-action related to the content

8. Additional Resources:
   - Create a "Further Reading" section with 5-7 relevant resources (articles, books, or websites)
   - Explain how each resource adds value to the reader's understanding of {topic}

9. SEO Optimization:
   - List primary and secondary keywords to be naturally incorporated throughout the listicle
   - Provide meta description options (under 160 characters) for the listicle

10. Social Sharing:
    - Suggest 5 "shareable" snippets from the listicle that would work well as social media posts
    - Recommend relevant hashtags for each shareable snippet

Throughout the listicle:
- Ensure the content is tailored to the interests and knowledge level of {audience}
- Consider the specified timeframe ({timeframe}) and its impact on the relevance of the information
- Incorporate insights from the Spider Graph analysis to add depth and authority to the content
- Address all relevant areas of emphasis: {', '.join(emphasis_areas)}
- Maintain a consistent tone and style that is both informative and engaging

Your goal is to create a comprehensive, engaging, and highly shareable listicle that provides valuable insights on {topic} while being optimized for both reader engagement and search engine visibility.
""",
        "Write an Instagram Post": f"""
Create an engaging and visually descriptive Instagram post about {topic} for {audience}. Your post should include:

1. Visual Description:
   - Describe in detail an eye-catching image or carousel of images (up to 10) that would accompany the post
   - Explain how each visual element relates to {topic} and appeals to {audience}
   - Suggest any text overlays, graphics, or design elements to be included in the images

2. Caption:
   - Write a compelling caption (max 2200 characters) that:
     a) Hooks the reader with an intriguing opening line
     b) Provides valuable information or insights related to {topic}
     c) Incorporates key points from the Spider Graph analysis
     d) Uses a tone and style appropriate for Instagram and the target audience
     e) Includes line breaks and emojis for readability and engagement
     f) Ends with a strong call-to-action or question to encourage engagement

3. Hashtags:
   - Provide a set of 15-30 relevant hashtags, including:
     a) Popular hashtags related to {topic}
     b) Niche hashtags specific to {audience}
     c) Branded hashtags (suggest potential branded hashtags if not provided)
     d) Trending hashtags that are relevant to the content
   - Explain the strategy behind your hashtag selection

4. Engagement Prompts:
   - Suggest 3-5 questions or prompts to include in the caption or first comment to encourage audience interaction

5. Story Content:
   - Propose 3-5 Instagram Story slides that complement the main post, including:
     a) Brief description of visual content for each slide
     b) Any text overlays or interactive elements (e.g., polls, quizzes, sliders)
     c) How each story slide relates to and expands upon the main post

6. Reels Concept:
   - Outline a 15-30 second Reels video concept that aligns with the post, including:
     a) Brief scene-by-scene breakdown
     b) Suggested music or sound effects
     c) Key points to be conveyed in text overlays

7. IGTV/Long-form Video Idea:
   - Propose a 2-3 minute IGTV or long-form video concept that dives deeper into {topic}, including:
     a) Outline of main talking points
     b) Suggestions for visual aids or demonstrations
     c) How to repurpose content from the main post and stories

8. Collaboration Opportunities:
   - Suggest 2-3 potential influencers or brands to collaborate with on this post, explaining why they would be a good fit

9. Cross-platform Sharing:
   - Provide ideas for how to repurpose this Instagram content for other social media platforms (e.g., Twitter, TikTok, LinkedIn)

10. Timing and Frequency:
    - Recommend the best time to post based on {audience} and {topic}
    - Suggest a follow-up posting schedule to create a series or campaign around this topic

Throughout the Instagram post plan:
- Ensure all elements are tailored to appeal to {audience}
- Consider the specified timeframe ({timeframe}) and its relevance to the content
- Incorporate insights from the Spider Graph analysis to make the post more informative and data-driven
- Address all relevant areas of emphasis: {', '.join(emphasis_areas)}
- Focus on creating visually appealing and highly engaging content that encourages shares and saves

Your goal is to create a comprehensive Instagram content plan that effectively communicates key information about {topic} while maximizing engagement and reach on the platform.
"""
    }

    return base_prompt + task_specific_prompts[task]