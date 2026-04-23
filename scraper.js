const gplay = require('google-play-scraper');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const path = require('path');

const csvWriter = createCsvWriter({
  path: path.join(__dirname, 'data', 'raw_reviews.csv'),
  header: [
    { id: 'date', title: 'date' },
    { id: 'rating', title: 'rating' },
    { id: 'title', title: 'title' },
    { id: 'review_text', title: 'review_text' },
    { id: 'platform', title: 'platform' }
  ]
});

async function scrapeReviews() {
  console.log('Fetching reviews from Play Store...');
  try {
    const reviews = await gplay.reviews({
      appId: 'com.openai.chatgpt',
      country: 'in',
      lang: 'en',
      num: 200,
      sort: gplay.sort.NEWEST
    });

    const records = reviews.data.map(r => ({
      date: new Date(r.date).toISOString().split('T')[0],
      rating: r.score,
      title: (r.title || '').replace(/[\n\r,]/g, ' ').trim(),
      review_text: (r.text || '').replace(/[\n\r,]/g, ' ').trim(),
      platform: 'android'
    }));

    await csvWriter.writeRecords(records);
    console.log(`Saved ${records.length} reviews to data/raw_reviews.csv`);
  } catch (err) {
    console.error('Scraper error:', err.message);
    process.exit(1);
  }
}

scrapeReviews();
