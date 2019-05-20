function loadCardsFilters() {
    let form = $('[id="filter-form-card"]');
    if (!form.data('loaded-separators')) {
        formShowMore(form, 'type', true, 'ordering', false);
    }
}

function loadCard() {
    $('[data-open-tab]').each(function() {
	$(this).unbind('click');
	$(this).click(function(e) {
	    $('[data-tabs="' + $(this).closest('.btn-group').data('control-tabs') + '"] .tab-pane').removeClass('active');
	    $('[data-tab="' + $(this).data('open-tab') + '"]').addClass('active');
	    $(this).blur();
	});
    });
}
