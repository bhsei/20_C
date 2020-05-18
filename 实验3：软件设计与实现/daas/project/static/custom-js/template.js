/*jshint esversion: 6 */

function load_nav(items, hrefs) {
    let breadcrumb = $('.breadcrumb');
    for (let i = 0; i < items.length; i++) {
        let li = document.createElement('li');
        if (i == items.length - 1) {
            li.classList.add('active');
            li.innerText = items[i];
        } else {
            let a = document.createElement('a');
            a.setAttribute('href', hrefs[i]);
            a.innerText = items[i];
            li.appendChild(a);
        }
        breadcrumb.append(li);
    }
}

/*function item_map(item){
    let map_dict = {
        '首页': '/project/',
        '项目': '/project/'
    };
    if(map_dict.hasOwnProperty(item))
        return map_dict[item];
    else
        return '#';
}*/