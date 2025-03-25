from pytrends.request import TrendReq
import random

class SEOOptimizer:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        # Expanded list of meme-specific keywords
        self.meme_related_keywords = [
            'memes', 'dank memes', 'funny memes', 'viral memes', 
            'tiktok memes', 'reddit memes', 'gaming memes',
            'anime memes', 'trending memes', 'meme compilation'
        ]
        # Keywords to ensure topic is meme-related
        self.meme_filters = ['meme', 'memes', 'funny', 'dank', 'viral', 'trend']

    def is_meme_related(self, term):
        """Check if a term is related to memes"""
        term_lower = term.lower()
        # Check if term contains any meme-related words
        return any(filter_word in term_lower for filter_word in self.meme_filters)

    def get_trending_topics(self):
        try:
            all_trending_terms = set()
            
            # Get trends for each meme keyword in batches of 5 (Google Trends limit)
            for i in range(0, len(self.meme_related_keywords), 5):
                keyword_batch = self.meme_related_keywords[i:i+5]
                self.pytrends.build_payload(
                    kw_list=keyword_batch,
                    cat=24,  # Entertainment category
                    timeframe='now 1-d',
                    geo='',
                    gprop='youtube'  # YouTube specific trends
                )
                
                # Get both top and rising queries
                related_queries = self.pytrends.related_queries()
                
                for kw in keyword_batch:
                    if kw in related_queries:
                        # Add top queries
                        if 'top' in related_queries[kw] and not related_queries[kw]['top'].empty:
                            terms = related_queries[kw]['top']['query'].tolist()
                            all_trending_terms.update([t for t in terms if self.is_meme_related(t)])
                            
                        # Add rising queries
                        if 'rising' in related_queries[kw] and not related_queries[kw]['rising'].empty:
                            terms = related_queries[kw]['rising']['query'].tolist()
                            all_trending_terms.update([t for t in terms if self.is_meme_related(t)])

            # If no meme-related trends found, use backup topics
            if not all_trending_terms:
                backup_topics = [
                    "Dank Memes", "Viral Memes", "TikTok Memes",
                    "Gaming Memes", "Anime Memes", "Reddit Memes",
                    "Trending Memes", "Latest Memes", "Popular Memes"
                ]
                return backup_topics

            return list(all_trending_terms)
            
        except Exception as e:
            print(f"Error fetching trends: {e}")
            return ["Dank Memes"]  # Fallback option

    def generate_title(self, is_short=False):
        trending = self.get_trending_topics()
        
        title_templates = [
            "ULTIMATE {trend} MEMES 🤣 Try Not To Laugh",
            "BEST {trend} Meme Compilation 😂",
            "FUNNIEST {trend} Memes of 2024! 🔥",
            "VIRAL {trend} Memes That Break The Internet",
            "{trend} Memes That Are Actually Funny 💀",
            "God Tier {trend} Memes 🎮",
            "These {trend} Memes Will Make Your Day 😂"
        ]
        
        short_templates = [
            "🤣 {trend} Memes #shorts",
            "Watch These {trend} Memes 😂 #shorts",
            "VIRAL {trend} Meme Moment 🔥 #shorts",
            "Best {trend} Memes RN 💀 #shorts",
            "{trend} Memes Be Like 😂 #shorts"
        ]
        
        templates = short_templates if is_short else title_templates
        template = random.choice(templates)
        trend = random.choice(trending)
        
        # Remove "meme" or "memes" from trend if it's already in the template
        trend = trend.replace(" meme", "").replace(" memes", "").strip()
        
        return template.format(trend=trend.title())

    def generate_tags(self, is_short=False):
        trending = self.get_trending_topics()
        
        # Base tags with meme-specific focus
        base_tags = [
            'memes', 'dank memes', 'funny memes', 'viral memes',
            'try not to laugh', 'meme compilation', 'best memes',
            'trending memes', 'funny videos', 'viral videos'
        ]
        
        if is_short:
            base_tags = ['shorts', 'short video', 'viral shorts'] + base_tags
        
        # Process trending terms into tags
        trend_tags = []
        for term in trending:
            # Add the term itself
            trend_tags.append(term.lower())
            # Add term + "memes" if "memes" is not already in it
            if "meme" not in term.lower():
                trend_tags.append(f"{term.lower()} memes")
        
        # Combine and remove duplicates while preserving order
        all_tags = []
        seen = set()
        for tag in (base_tags + trend_tags):
            if tag not in seen:
                all_tags.append(tag)
                seen.add(tag)
        
        # Limit to YouTube's 500-character limit
        final_tags = []
        char_count = 0
        for tag in all_tags:
            if char_count + len(tag) + 1 <= 500:  # +1 for the comma
                final_tags.append(tag)
                char_count += len(tag) + 1
            else:
                break
                
        return final_tags 