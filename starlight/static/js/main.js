// *****************************************
// *****************************************
// MagiCircles
// *****************************************
// *****************************************

// *****************************************
// Accounts / leaderboard

function loadAccountsFilters() {
    loadAccounts();
    let form = $('[id="filter-form-account"]');
    if (!form.data('loaded-separators')) {
        form.data('loaded-separators', true);
        formShowMore(form, 'i_version', false, 'ordering', false);
    }
}

// *****************************************
// Users

function loadUsersFilters() {
    let form = $('[id="filter-form-user"]');
    if (!form.data('loaded-separators')) {
        form.data('loaded-separators', true);
        formShowMore(form, 'color', true, 'ordering', false);
    }
}

// *****************************************
// Activities

function loadActivities() {
    updateActivities();
    $('.activity').each(function () {
        let activity = $(this);
        if (!activity.data('loaded-activity')) {
            activity.data('loaded-activity', true);
            // Show Revue Starlight International as activity author when Revue_EN
            if (activity.find('.owner').text() == 'Revue_EN') {
                activity.find('.owner').text('Revue Starlight International');
                // Load cards details in place of cards tags
                if ($(document).width() > 768) {
                    $.each([
                        ['card', loadBaseCard],
                        ['memoir', loadBaseCard],
                        ['event', undefined],
                    ], function(_i, item) {
                        activity.find('.message a[href*="/' + item[0] + '/"]').each(function() {
                            let a = $(this);
                            // Only if a doesn't contain HTML and is alone on its line.
                            if (a.has('*').length == 0 && $.trim(a.closest('p').text()) == $.trim(a.text())) {
                                let url_parts = a.prop('href').replace(
                                    '/' + item[0] + '/', '/ajax/' + item[0] + '/').split('/');
                                url_parts = url_parts.splice(0, url_parts.length - 2)
                                let url = url_parts.join('/') + '/';
                                $.ajax({
                                    type: 'GET',
                                    url: url,
                                    success: function(data) {
                                        a.replaceWith('<div class="well fontx0-8">' + data + '</div>');
                                        if (typeof(item[1]) != 'undefined') {
                                            item[1]();
                                        }
                                        loadCommons();
                                        cropActivityWhenTooLong(activity);
                                    },
                                    // Fails silently
                                });
                            }
                        });
                    });
                }
            }
        }
    });
}

// *****************************************
// *****************************************
// Revue Starlight
// *****************************************
// *****************************************

// *****************************************
// Staff

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

// *****************************************
// Song

function loadSong() {
    $('.item-info.song-info').each(function () {
        let song = $(this);
        if (!song.data('loaded-song')) {
            song.data('loaded-song', true);
            loadAlliTunesData();
            function toggleLyrics(field, button, animation) {
                let caret = button.find('.glyphicon');
                let text = button.find('.text-open');
                if (caret.hasClass('glyphicon-triangle-bottom')) {
                    caret.removeClass('glyphicon-triangle-bottom');
                    caret.addClass('glyphicon-triangle-top');
                    text.text(gettext('Close'));
                    field.find('.long-text-value').show(animation);
                } else {
                    caret.removeClass('glyphicon-triangle-top');
                    caret.addClass('glyphicon-triangle-bottom');
                    text.text(gettext('Open {thing}').replace('{thing}', gettext('Lyrics').toLowerCase()));
                    field.find('.long-text-value').hide(animation);
                }
            }
            song.find('[data-field$="lyrics"]').each(function() {
                let field = $(this);
                let button = $('<a href="#show" class="pull-right padding20"><p><span class="glyphicon glyphicon-triangle-top"></span> <span class="text-open"></span></p></a>');
                field.find('.long-text-title').before(button);
                toggleLyrics(field, button);
                button.click(function(e) {
                    e.preventDefault();
                    toggleLyrics(field, button, 'fast');
                    return false;
                });
            });
        }
    });
}

// *****************************************
// *****************************************
// Relive
// *****************************************
// *****************************************

// *****************************************
// Cards

function loadCardsFilters() {
    let form = $('[id="filter-form-card"]');
    if (!form.data('loaded-separators')) {
        form.data('loaded-separators', true);
        formShowMore(form, 'type', true, 'ordering', false);
    }
}

function loadBaseCard() {
    $('.item-info.card-info, .item-info.memoir-info').each(function() {
        let card = $(this);
        if (!card.data('loaded-card')) {
            card.data('loaded-card', true);
            // Load statistics tabs
            card.find('[data-open-tab]').each(function() {
    	        $(this).unbind('click');
    	        $(this).click(function(e) {
    	            $('[data-tabs="' + $(this).closest('.btn-group').data('control-tabs') + '"] .tab-pane').removeClass('active');
    	            $('[data-tab="' + $(this).data('open-tab') + '"]').addClass('active');
    	            $(this).blur();
    	        });
            });
            // Load icons selector
            let all_icons = card.find('[data-field="icon"] [data-rank]');
            let all_ranks = getAllValues(all_icons, 'data-rank').map(n => parseInt(n));
            let all_rarities = getAllValues(all_icons, 'data-rarity').map(n => parseInt(n));
            var current_rank = all_ranks[all_ranks.length - 1];
            var current_rarity = 0;
            var rarity_selector = 0;
            let selectors = $('<div style="display: inline-block;" class="padding10"></div>');
            card.find('[data-field="icon"] td').last().prepend(selectors);
            let selector_template = '<span><a href="#previous"><span class="glyphicon glyphicon-triangle-left text-muted fontx0-8"></span></a> <span style="display: inline-block; text-align: center; width: 100px;"><img src="#" height="20"></span> <a href="#next"><span class="glyphicon glyphicon-triangle-right text-muted fontx0-8"></span></a></span>';
            let rank_selector = $(selector_template);
            rank_selector.find('a[href="#previous"]').click(function(e) {
                e.preventDefault();
                current_rank = current_rank - 1;
                if (!all_ranks.includes(current_rank)) {
                    current_rank = all_ranks[all_ranks.length - 1];
                }
                iconToggler();
                return false;
            });
            rank_selector.find('a[href="#next"]').click(function(e) {
                e.preventDefault();
                current_rank = current_rank + 1;
                if (!all_ranks.includes(current_rank)) {
                    current_rank = all_ranks[0];
                }
                iconToggler();
                return false;
            });
            selectors.append(rank_selector);
            if (all_rarities.length > 0) {
                current_rarity = all_rarities[0];
                rarity_selector = $(selector_template);
                rarity_selector.find('a[href="#previous"]').click(function(e) {
                    e.preventDefault();
                    current_rarity = current_rarity - 1;
                    if (!all_rarities.includes(current_rarity)) {
                        current_rarity = all_rarities[all_rarities.length - 1];
                    }
                    iconToggler();
                    return false;
                });
                rarity_selector.find('a[href="#next"]').click(function(e) {
                    e.preventDefault();
                    current_rarity = current_rarity + 1;
                    if (!all_rarities.includes(current_rarity)) {
                        current_rarity = all_rarities[0];
                    }
                    iconToggler();
                    return false;
                });
                selectors.append('<br>');
                selectors.append(rarity_selector);
            }
            function iconToggler() {
                all_icons.hide();
                rank_selector.find('img').prop('src', static_url + 'img/' + (all_ranks.includes(7) ? '' : 'memoir_') + 'rank/' + current_rank + '.png');
                rank_selector.find('img').prop('alt', current_rank);
                if (all_rarities.length > 0) {
                    rarity_selector.find('img').prop('src', static_url + 'img/small_rarity/' + current_rarity + '.png');
                    rarity_selector.find('img').prop('alt', current_rarity);
                    all_icons.filter('[data-rank="' + current_rank + '"][data-rarity="' + current_rarity + '"]').show();
                } else {
                    all_icons.filter('[data-rank="' + current_rank + '"]').show();
                }
            }
            iconToggler();
        }
    });
}

function loadBaseCardForm() {
    let form = $('[data-form-name="add_card"], [data-form-name="edit_card"], [data-form-name="add_memoir"], [data-form-name="edit_memoir"]');
    if (!form.data('loaded')) {
        form.data('loaded', true);
        // Acts
        let acts = form.find('#id_acts');
        if (acts.length == 1) {
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
        // Statistics
        formShowMore(form, 'base_hp', true, 'max_level_agility', false, 'Show statistics fields', 'Hide statistics fields', false);
        // Icons
        if ($('#id_rank1_rarity2_icon').length > 0) {
            formShowMore(form, 'rank1_rarity2_icon', true, 'rank7_rarity6_icon', false, 'Show icons fields', 'Hide icons fields', false);
        }
    }
}

// *****************************************
// Acts

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
