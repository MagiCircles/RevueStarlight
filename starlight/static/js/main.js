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
