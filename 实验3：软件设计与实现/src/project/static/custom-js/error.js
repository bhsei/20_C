function show_error_msg(pos, error_msg){
    let error_div = document.createElement('div');
    error_div.classList.add('error-info');

    let i = document.createElement('i');
    i.setAttribute('class', 'fa fa-exclamation-triangle');
    i.setAttribute('aria-hidden', 'true');
    error_div.appendChild(i);

    let p = document.createElement('p');
    p.setAttribute('class', 'error-text');
    p.innerText = error_msg;
    error_div.appendChild(p);

    let form_item = $('.form-item')[pos-1];
    form_item.after(error_div);
}