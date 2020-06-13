/*jshint esversion: 6 */

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

function clear_error_feedback(target_input, parent_div) {
    $(target_input).closest(parent_div).children().filter('span').remove();
    $(target_input).closest(parent_div).removeClass('has-error has-feedback');
}

function set_error_feedback(target_input, parent_div, error_msg) {
    let parentDiv = $(target_input).closest(parent_div);
    parentDiv.addClass('has-error has-feedback');

    if (target_input.type != 'file') {
        let cross_icon = document.createElement('span');
        cross_icon.setAttribute('class', 'glyphicon glyphicon-remove form-control-feedback');
        cross_icon.setAttribute('aria-hidden', 'true');
        parentDiv.append(cross_icon);
    }

    let exclamation_icon = document.createElement('span');
    exclamation_icon.setAttribute('class', 'fa fa-exclamation-triangle form-error');
    parentDiv.append(exclamation_icon);

    let error_text = document.createElement('span');
    error_text.setAttribute('class', 'form-error');
    error_text.innerText = ' '+error_msg;
    parentDiv.append(error_text);
}