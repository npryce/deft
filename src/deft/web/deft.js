$(function() {
    var features = $('.deft-features ol');
    features.sortable({
        connectWith: '.deft-features ol',
	placeholder: 'deft-drag-placeholder',
	revert: true
    });
    features.disableSelection();
});
