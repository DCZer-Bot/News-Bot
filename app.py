import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random
from PIL import Image, ImageDraw, ImageFont
import io

# ------------------- CONFIG -------------------
TOKEN = ""  # Replace with your bot token
DATA_FILE = "news_data.json"

# Ensure data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_news():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_news(news_list):
    with open(DATA_FILE, "w") as f:
        json.dump(news_list, f, indent=4)

# ------------------- BOT SETUP -------------------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)  # prefix not used for slash commands

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Slash commands synced!")

# ------------------- COMMANDS -------------------

# /createnews
@bot.tree.command(name="createnews", description="Create a news entry (text only)")
@app_commands.describe(
    headlines="The main headline",
    summary="A short summary",
    category="Category (e.g., Tech, Sports, World)"
)
async def createnews(interaction: discord.Interaction, headlines: str, summary: str, category: str):
    news_list = load_news()
    news_item = {
        "headlines": headlines,
        "summary": summary,
        "category": category,
        "author": str(interaction.user)
    }
    news_list.append(news_item)
    save_news(news_list)
    embed = discord.Embed(
        title="📰 News Created",
        description=f"**Headlines:** {headlines}\n**Summary:** {summary}\n**Category:** {category}",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

# /bignews – generates an image with the news using PIL
@bot.tree.command(name="bignews", description="Create a news entry AND generate an image with it")
@app_commands.describe(
    headlines="The main headline",
    summary="A short summary",
    category="Category (e.g., Tech, Sports, World)"
)
async def bignews(interaction: discord.Interaction, headlines: str, summary: str, category: str):
    # Save the news first (same as /createnews)
    news_list = load_news()
    news_item = {
        "headlines": headlines,
        "summary": summary,
        "category": category,
        "author": str(interaction.user)
    }
    news_list.append(news_item)
    save_news(news_list)

    # Generate an image
    await interaction.response.defer()  # Because image generation may take a moment

    try:
        # Create a blank image (800x400, dark background)
        img = Image.new('RGB', (800, 400), color=(30, 30, 40))
        draw = ImageDraw.Draw(img)

        # Try to load a font, fallback to default
        try:
            font_title = ImageFont.truetype("arial.ttf", 32)
            font_text = ImageFont.truetype("arial.ttf", 24)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()

        # Draw a border
        draw.rectangle([(10, 10), (790, 390)], outline=(255, 215, 0), width=3)

        # Write text
        draw.text((30, 30), f"📰 {headlines}", fill=(255, 255, 255), font=font_title)
        draw.text((30, 100), f"Summary: {summary}", fill=(200, 200, 200), font=font_text)
        draw.text((30, 160), f"Category: {category}", fill=(100, 200, 255), font=font_text)

        # Save image to memory
        with io.BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.followup.send(
                content=f"✅ News created and image generated!",
                file=discord.File(fp=image_binary, filename='news.png')
            )
    except Exception as e:
        await interaction.followup.send(f"❌ Image generation failed: {str(e)}")

# /help
@bot.tree.command(name="help", description="Show all available commands")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📰 News Bot Help",
        description="Here are the slash commands you can use:",
        color=discord.Color.blue()
    )
    embed.add_field(name="/createnews", value="Create a text-only news entry.", inline=False)
    embed.add_field(name="/bignews", value="Create a news entry and generate an image with it.", inline=False)
    embed.add_field(name="/dailynews", value="Show a random news from the stored list.", inline=False)
    embed.add_field(name="/indev", value="Show the GitHub repository of this bot.", inline=False)
    embed.add_field(name="/help", value="Show this help message.", inline=False)
    await interaction.response.send_message(embed=embed)

# /indev
@bot.tree.command(name="indev", description="Show the bot's GitHub repository")
async def indev(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔧 Bot Repository",
        description="This bot is under development. Source code:",
        url="https://github.com/DCZer-Bot/News-Bot",
        color=discord.Color.purple()
    )
    embed.add_field(name="GitHub", value="[Click here](https://github.com/DCZer-Bot/News-Bot)", inline=False)
    await interaction.response.send_message(embed=embed)

# /dailynews – random news
@bot.tree.command(name="dailynews", description="Show a random news entry")
async def dailynews(interaction: discord.Interaction):
    news_list = load_news()
    if not news_list:
        await interaction.response.send_message("❌ No news available yet. Use `/createnews` or `/bignews` to add some!")
        return
    random_news = random.choice(news_list)
    embed = discord.Embed(
        title=f"📰 Daily News: {random_news['headlines']}",
        description=random_news['summary'],
        color=discord.Color.gold()
    )
    embed.add_field(name="Category", value=random_news['category'], inline=True)
    embed.add_field(name="Author", value=random_news.get('author', 'Unknown'), inline=True)
    await interaction.response.send_message(embed=embed)

# ------------------- RUN BOT -------------------
if __name__ == "__main__":
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Please set your bot token in the TOKEN variable.")
    else:
        bot.run(TOKEN)