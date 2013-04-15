var totElements = 0;
function clipbox(data)
{
    //data = [{"meta": "for p in pasteL... (248 chars)", "type": "text", "id": "2012-01-14_17-20-18OZJU83", "time": 1326561618},
    //           {"meta": "217x111 pixels (5.0K)", "type": "image", "id": "AZPQU0_2012-01-14_17-20-35AWVVBV.png", "time": 1326561635}]
    totElements = 0;
    tbodyHtml = "";
    
    data.sort(function(a, b) {
        return parseInt(b['time']) - parseInt(a['time']);
    });
    
    for(var d=0; d<data.length; d++)
    {
        totElements += 1;
        var retURL = "http://dl.dropbox.com/u/"+localStorage['user']+"/.clipbox/"+data[d]['id'];

        var actions = "<a target='_blank' href='"+retURL+"'>View</a>";
        
        //actions += "<br /><a data-pasteurl='"+retURL+"' class='pasteurl' id='phrefid"+totElements+"'>Copy URL</a>";
        
        if (data[d]['type'] == 'text')
        {
            if (data[d]['meta'].replace(/^\s+|\s+$/g,"").substring(0,4) == 'http') //strip whitespace, check first 4 chars
            {
                //this is a url. Maybe. We could use some better regex to check, lulz.
                data[d]['type'] = "url";
                actions += "<br /><a onclick='load_url(\""+retURL+"\");return false;' href=''>GOTO Paste</a>";
            }
        }
        /*
        if (data[d]['type'] == 'text')
        {
            actions += "<br /><a onclick='load_paste(\""+retURL+"\");return false;' href=''>Copy Paste</a>";
        }
        */
        
        tbodyHtml += " <tr id='rowid_"+totElements+"'> <td>"+data[d]['type']+"</td> <td>Meta: "+htmlEscape(data[d]['meta'])+"<br />"+get_time(data[d]['time'])+"</td><td>"+actions+"</td></tr>";
    }
    document.getElementById('plist').innerHTML = tbodyHtml;
    
    $("a.pasteurl").each(function() {
        var clip = new ZeroClipboard.Client();
        clip.setHandCursor( true );
        clip.glue($(this).attr('id'));
        clip.setText($(this).attr('data-pasteurl'));
        clip.addEventListener('complete', function(client, text) {
            document.getElementById('msg').innerHTML = "<font color=green>URL Copied to clipboard!</font><br /><br />";
        });
    });
}

/************Login**********/
function login()
{
    var url = "http://dl.dropbox.com/u/"+document.getElementById('dbid').value+"/.clipbox/."+md5('Royale.'+document.getElementById('password').value);
    localStorage['authurl'] = url;
    localStorage['user'] = document.getElementById('dbid').value;
    load_db_js(url);
}
function load_db_js(url)
{
    add_script_to_page(url);
}
function check_for_login()
{
    if(typeof localStorage['authurl'] === "undefined")
    {
        //do nothing
    }
    else
    {
        load_db_js(localStorage['authurl']);
    }
}


/*********YQL**********/
function yql_it(url, callback)
{
    yql("select * from html where url='"+url+"'", callback);
}
function yql(query, callback)
{
    var url = 'http://query.yahooapis.com/v1/public/yql?q='+encodeURIComponent(query.toLowerCase())+'&format=json&callback='+callback; 
    add_script_to_page(url);
}
function extract_paste_from_yql(data)
{
    var result = "";
    for (h in data.query.results.body)
    {
        result = data.query.results.body[h];
    }
    return result;
}
function load_paste(url)
{
    yql_it(url, "load_paste_callback");
}

function load_url(url)
{
    yql_it(url, "load_url_callback");
}
//var window_name=0;
function load_url_callback(data)
{
    //window_name += 1;
    //window.open(extract_paste_from_yql(data),'_newtab'+window_name);
    document.location.href = extract_paste_from_yql(data);
}
function load_paste_callback(data)
{
    copy_paste(extract_paste_from_yql(data));
}

/***********Invoke Copy Command**************/
function copy_url(text)
{
    copy(text);
    document.getElementById('msg').innerHTML = "<font color=green>URL Copied to clipboard!</font><br /><br />";
}
function copy_paste(text)
{
    copy(text);
    document.getElementById('msg').innerHTML = "<font color=blue>Paste Copied to clipboard!</font><br /><br />";
}
function copy(text)
{
    chrome.extension.getBackgroundPage().copyme(text);
}

/**************Misc. Helper functions***********/
function get_time(unix_timestamp)
{
    var date = new Date(unix_timestamp*1000);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString();
}
function add_script_to_page(url)
{
    var head = document.getElementsByTagName("head")[0];
    var scriptEl = document.createElement("script");
    scriptEl.type = "text/javascript";
    scriptEl.src = url;
    head.appendChild(scriptEl);
}
function htmlEscape(str)
{
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}