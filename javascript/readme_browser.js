
var readme_browser_subFilePath = undefined;

function readme_browser_openSubFile_(dummy, extPath) {
    return [readme_browser_subFilePath, extPath];
}


function readme_browser_openSubFile(filePath) {
    readme_browser_subFilePath = filePath;
    button = gradioApp().getElementById('readme_browser_openSubFileButton');
    button.click();
}


function readme_browser_convertUrls() {
    file = gradioApp().getElementById('readme_browser_file');
    hElements = [...file.querySelectorAll("h1, h2, h3, h4, h5, h6")];
    let anchorNumbers = {};
    hElements.forEach((h) => {
        if (!h.innerHTML) return;
        let anchor = document.createElement('a');
        let anchorID = h.innerHTML.toLowerCase().replaceAll(' ', '-');
        if (anchorID in anchorNumbers) {
            let key = anchorID;
            anchorID += '-' + anchorNumbers[key];
            anchorNumbers[key] += 1;
        } else {
            anchorNumbers[anchorID] = 1;
        }
        anchor.setAttribute('id', anchorID);
        h.parentNode.insertBefore(anchor, h);
    });

    aElements = [...file.getElementsByTagName('a')];
    if (!aElements) return;

    aElements.forEach((a) => {
        if (!a.href) return;
        const url = new URL(a.href);
        if (url.origin === window.location.origin && a.href.indexOf('#') !== -1) {
            a.setAttribute('target', '');
            return;
        }
        const prefix = 'readme_browser_javascript_';
        const prefixIndex = a.href.indexOf(prefix);
        if (prefixIndex !== -1) {
            a.setAttribute('onclick', a.href.slice(prefixIndex + prefix.length));
            a.setAttribute('target', '');
            a.href = '#';
        }
    });
}

