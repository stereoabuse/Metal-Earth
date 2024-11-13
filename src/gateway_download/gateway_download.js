// Load the pages from Tolkien Gateway into a JSON file 
// Must enter this in the Chrome console, see `data/tolkien_gateway_download_process.md` for more details

async function getAllPages(apiUrl = '/w/api.php') {
    let allPages = [];
    let apcontinue = '';
    
    while (true) {
      const params = {
        action: 'query',
        list: 'allpages',
        aplimit: 500, // Get maximum number of pages per request
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
        
        // Add the current batch of pages
        const pages = data.query.allpages.map(page => page.title);
        allPages = allPages.concat(pages);
  
        // Check if there are more pages to fetch
        if (data.continue && data.continue.apcontinue) {
          apcontinue = data.continue.apcontinue;
          console.log(`Fetched ${allPages.length} pages so far...`);
        } else {
          break; // No more pages to fetch
        }
  
        // Optional: Add a small delay to avoid hitting rate limits
        await new Promise(resolve => setTimeout(resolve, 100));
  
      } catch (error) {
        console.error('Error fetching pages:', error);
        break;
      }
    }
  
    console.log(`Completed! Total pages fetched: ${allPages.length}`);
    return allPages;
  }
  
  // Optional: Function to save the results to a file (if running in Node.js)
  async function saveToFile(pages, filename = 'all_pages.json') {
    const fs = require('fs').promises;
    await fs.writeFile(filename, JSON.stringify(pages, null, 2));
    console.log(`Saved ${pages.length} pages to ${filename}`);
  }
  
  
  window.wikiPages = null;
  getAllPages('https://tolkiengateway.net/w/api.php').then(pages => {
      window.wikiPages = pages;
      console.log('Pages stored in window.wikiPages');
  });
  
  const blob = new Blob([JSON.stringify(wikiPages, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'wiki_pages.json';
  a.click();