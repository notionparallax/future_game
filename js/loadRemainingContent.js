document.addEventListener("DOMContentLoaded", function (event) {
    var url = "/index-data.json";

    makeRequest("GET", url)
        .then(function (datums) {
            // console.log(datums);
            replacePosts(JSON.parse(datums));
        })
        .catch(function (err) {
            console.error("Augh, there was an error!", err.statusText);
        });

    function replacePosts(theJSON) {
        let newInnerHTML = "";

        for (let p of theJSON) {
            let liTemplate = `
            <li itemscope itemtype="http://schema.org/BlogPosting">
              <span class="post-date">${p.pretty_date || " "}</span>
              <meta itemprop="datePublished" content="${p.date || " "}" />
              <meta itemprop="dateModified" content="${p.date || " "}" />
              <span itemprop="author" itemscope itemtype="http://schema.org/Person">
                <span itemprop="name" content="${p.author || " "}"></span>
              </span>

              <span itemprop="publisher" itemscope itemtype="https://schema.org/Organization">
                <span itemprop="logo" itemscope itemtype="https://schema.org/ImageObject">
                  <meta itemprop="url" content="https://upload.wikimedia.org/wikipedia/commons/9/9e/Sus_scrofa_avionica.png">
                  <meta itemprop="width"  content="700">
                  <meta itemprop="height" content="500">
                </span>
              <meta itemprop="name" content="Notion Parallax">
              </span>

              <span itemprop="image" itemscope itemtype="https://schema.org/ImageObject">
                <meta itemprop="url" content="https://upload.wikimedia.org/wikipedia/commons/9/9e/Sus_scrofa_avionica.png">
                  <meta itemprop="width"  content="700">
                  <meta itemprop="height" content="500">
              </span>

              <h2 itemprop="headline">
                <a itemprop="mainEntityOfPage"  class="post-link" href="${
                    p.url || " "
                }">${p.title || " "}</a>
              </h2>

              <p itemprop="description">${p.description || ">_"}</p>
            </li>`;
            newInnerHTML += liTemplate;
        }

        let postList = document.getElementsByClassName("post-list").item(0);
        postList.innerHTML = newInnerHTML;
        console.log("Added the extra posts");
    }
});
