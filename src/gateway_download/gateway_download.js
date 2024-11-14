// Must enter this in the Chrome console, see `data/external-sources/tolkien_gateway_download_process.md` for more details

// Fetch and Save all pages from Tolkien Gateway to a JSON file

async function getAllPages(apiUrl = '/w/api.php') {
  let allPages = [];
  let apcontinue = '';
  
  while (true) {
    const params = {
      action: 'query',
      list: 'allpages',
      aplimit: 500, // Maximum pages per request
      format: 'json',
      origin: '*',
      ...(apcontinue ? { apcontinue } : {})
    };

    const queryString = Object.entries(params)
      .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
      .join('&');

    const url = `${apiUrl}?${queryString}`;

    try {
      const response = await fetch(url);
      const data = await response.json();
      
      // Add pages from the current request
      const pages = data.query.allpages.map(page => page.title);
      allPages = allPages.concat(pages);

      // Continue if there are more pages to fetch
      if (data.continue && data.continue.apcontinue) {
        apcontinue = data.continue.apcontinue;
        console.log(`Fetched ${allPages.length} pages so far...`);
      } else {
        break; // No more pages
      }

      // Delay to avoid rate limits
      await new Promise(resolve => setTimeout(resolve, 100));

    } catch (error) {
      console.error('Error fetching pages:', error);
      break;
    }
  }

  console.log(`Completed! Total pages fetched: ${allPages.length}`);
  return allPages;
}

// Fetch pages and download as JSON
getAllPages('https://tolkiengateway.net/w/api.php').then(pages => {
  const blob = new Blob([JSON.stringify(pages, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'wiki_pages.json';
  a.click();
  console.log('Download initiated: wiki_pages.json');
});
