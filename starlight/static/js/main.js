function loadCardsFilters() {
    let form = $('[id="filter-form-card"]');
    if (!form.data('loaded-separators')) {
        form.data('loaded-separators', true);
        formShowMore(form, 'type', true, 'ordering', false);
    }
}

function loadBaseCard() {
    $('[data-open-tab]').each(function() {
	$(this).unbind('click');
	$(this).click(function(e) {
	    $('[data-tabs="' + $(this).closest('.btn-group').data('control-tabs') + '"] .tab-pane').removeClass('active');
	    $('[data-tab="' + $(this).data('open-tab') + '"]').addClass('active');
	    $(this).blur();
	});
    });
}

function loadBaseCardForm() {
    let acts = $('#id_acts').last();
    if (acts.length == 1 && !acts.data('loaded-show-more')) {
        acts.css('overflow', 'hidden');
        acts.css('height', 200);
        let buttons = acts.parent().find('.btn-group');
        let button = $('<a href="#showAll" target="_blank" class="btn btn-secondary">See all</a>');
        button.click(function(e) {
            e.preventDefault();
            acts.css('height', 'auto');
            button.remove();
            return false;
        });
        buttons.prepend(button);
    }

}

function loadActForm() {
    let form = $('[data-form-name="add_act"], [data-form-name="edit_act"]');
    let targetField = form.find('#id_i_target');
    let otherTargetField = form.find('#id_other_target');
    function otherTargetToggler(animation) {
        if (targetField.val() == 'other') {
            otherTargetField.closest('.form-group').show(animation);
        } else {
            otherTargetField.val('');
            otherTargetField.closest('.form-group').hide(animation);
        }
    }
    if (otherTargetField.val() != '') {
        targetField.val('other');
        targetField.closest('.form-group').find('.cuteform-elt').removeClass('cuteform-selected');
        targetField.closest('.form-group').find('[data-cuteform-val="other"]').addClass('cuteform-selected');
    }
    otherTargetToggler();
    targetField.change(function(e) {
        otherTargetToggler('fast');
    });
}

function loadAccountsFilters() {
    loadAccounts();
    let form = $('[id="filter-form-account"]');
    if (!form.data('loaded-separators')) {
        form.data('loaded-separators', true);
        formShowMore(form, 'i_version', false, 'ordering', false);
    }
}

function loadUsersFilters() {
    let form = $('[id="filter-form-user"]');
    if (!form.data('loaded-separators')) {
        form.data('loaded-separators', true);
        formShowMore(form, 'color', true, 'ordering', false);
    }
}

function loadStaff() {
    $('[data-field="description"]').each(function() {
        let descriptionTr = $(this);
        if (!descriptionTr.data('loaded-quote')) {
            let descriptionContent = descriptionTr.find('.long-text-value');
            if (descriptionContent.length) {
                let icon = $('<a href="#show" style="display: block;"></a>');
                descriptionContent.hide();
                descriptionTr.append(icon);
                icon.click(function(e) {
                    e.preventDefault();
                    icon.hide();
                    descriptionContent.show();
                    return false;
                });
                descriptionContent.click(function(e) {
                    e.preventDefault();
                    descriptionContent.hide();
                    icon.show();
                    return false;
                });
            }
            descriptionTr.data('loaded-quote', true);
        }
    });

}
