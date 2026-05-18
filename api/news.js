import news from "../data/news.json";

export default function handler(req, res) {
    const random = news[Math.floor(Math.random() * news.length)];

    res.status(200).json({
        success: true,
        news: random
    });
}