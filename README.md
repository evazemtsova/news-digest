# 🗞️ News Digest

A web application for aggregating and displaying posts from Telegram channels in a clean, organized interface.

## ✨ Features

- **Channel Management**: Add and manage Telegram channels with custom tags
- **Automated Parsing**: Daily automatic scraping of new posts via scheduled jobs
- **Tag-based Filtering**: Organize posts by categories (Tech, ML, Product, Lifestyle, Other)
- **Responsive Design**: Clean, GitHub-styled dark theme interface
- **Real-time Updates**: Fresh content delivered automatically

## 🚀 Live Demo

Visit the live application: [Your Vercel URL here]

## 🏗️ Architecture

- **Frontend**: Vanilla HTML, CSS, and JavaScript with responsive design
- **Backend**: Python serverless functions deployed on Vercel
- **Database**: Supabase PostgreSQL for storing channels and posts
- **Deployment**: Vercel with automated cron jobs
- **Web Scraping**: BeautifulSoup for parsing Telegram channel pages

## 📂 Project Structure

```
news-digest/
├── api/                    # Serverless API functions
│   ├── channels.py        # Channel CRUD operations
│   ├── posts.py          # Posts retrieval
│   └── parse.py          # Automated parsing logic
├── index.html            # Main web interface
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel deployment config
└── README.md           # This file
```

## 🛠️ Setup & Development

### Prerequisites

- Python 3.8+
- Supabase account
- Vercel account (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/evazemtsova/news-digest.git
   cd news-digest
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   Create a `.env` file with:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

4. **Database Setup**
   Create the following tables in your Supabase project:

   **channels table:**
   ```sql
   CREATE TABLE channels (
     id SERIAL PRIMARY KEY,
     username VARCHAR(255) NOT NULL UNIQUE,
     tag VARCHAR(50) NOT NULL DEFAULT 'other',
     created_at TIMESTAMP DEFAULT NOW()
   );
   ```

   **posts table:**
   ```sql
   CREATE TABLE posts (
     id SERIAL PRIMARY KEY,
     text TEXT NOT NULL,
     date TIMESTAMP,
     link TEXT NOT NULL UNIQUE,
     channel VARCHAR(255) NOT NULL,
     tag VARCHAR(50) NOT NULL,
     created_at TIMESTAMP DEFAULT NOW()
   );
   ```

5. **Run locally**
   For local development, you can use Vercel CLI:
   ```bash
   npx vercel dev
   ```

## 🚀 Deployment

### Deploy to Vercel

1. **Fork/Clone this repository**

2. **Connect to Vercel**
   - Import your GitHub repository in Vercel dashboard
   - Set environment variables in Vercel settings:
     - `SUPABASE_URL`
     - `SUPABASE_KEY`

3. **Deploy**
   - Vercel will automatically deploy on push to main branch
   - The cron job will run daily at 9:00 AM UTC

### Manual Deployment
```bash
vercel --prod
```

## 📡 API Endpoints

- `GET /api/posts` - Retrieve latest posts (limit 100)
- `GET /api/channels` - Get all registered channels
- `POST /api/channels` - Add new channel
- `DELETE /api/channels` - Remove channel
- `GET /api/parse` - Trigger manual parsing (runs automatically via cron)

## 🏷️ Supported Tags

- **Tech** - Technology and programming content
- **ML** - Machine Learning and AI posts
- **Product** - Product management and business
- **Lifestyle** - Lifestyle and personal content
- **Other** - General content

## 🔄 How It Works

1. **Channel Registration**: Users add Telegram channels with associated tags
2. **Automated Parsing**: Daily cron job scrapes new posts from registered channels
3. **Content Storage**: Posts are stored in Supabase with deduplication
4. **Web Interface**: Users browse and filter posts by tags
5. **Direct Links**: Click through to original Telegram posts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/evazemtsova/news-digest/issues) page
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## 🙏 Acknowledgments

- [Supabase](https://supabase.com/) for the backend infrastructure
- [Vercel](https://vercel.com/) for hosting and serverless functions
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) for web scraping capabilities