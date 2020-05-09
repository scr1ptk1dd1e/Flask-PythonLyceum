(function() {
    var lessons_html = '';
    var flickerAPI = "http://127.0.0.1:8080/api/student/lessons";
    $.getJSON(flickerAPI)
        .done(function( data ) {
            $.each( data.lessons, function(i, lesson) {
            lessons_html +=`
                <li class='lessons-list__item' style='cursor: pointer;'>
                    <a href='` + window.location.pathname + lesson.id + `' class='lessons-list__link'>
                        <div class='lesson-card'>
                            <div class='lesson-card__lesson col-6'>
                                <h4>` + lesson.title + `</h4>
                                <span>До 27 апреля</span>
                            </div>
                            <div class='lesson-card__progress col-6'>
                                <div class='progress'>
                                    <div class='progress-bar' style='width: 25%' aria-valuenow='25' aria-valuemin='0' aria-valuemax='100'>25%</div>
                                </div>
                                <span class='d-none d-sm-block'>0/` + lesson.numTasks + ` задач зачтено</span>
                            </div>
                        </div>
                    </a>
                </li>`;
        });
            $("#lessons-list").html(lessons_html);
        });
})();

$(function(){
    $(".lessons-list__item").hover(
    function() {
        $(this).addClass('shadow').css('cursor', 'pointer'); 
    }, function() {
        $(this).removeClass('shadow');
    }
);
});

/*
$(function(){
    $(".lessons-list__item").click(function(e) {
        window.history.pushState("TEST","Test", window.location.pathname + "/test");
    });
});
*/

$(function() {
    $(".lessons-list__link").click(function(e) {
        pageurl = $(this).attr('href');
        $.ajax({
            url: 'http://127.0.0.1:8080/api/student/' + pageurl,
            success: function(data) {
                console.log(data)
                $('.container').html(data);
            }
        });
        if (pageurl != window.location) {
            window.history.pushState({
                path: pageurl
            }, '', pageurl);
        }
        return false;
    });
});

$(window).bind('popstate', function() {
    $.ajax({
        url: 'http://127.0.0.1:8080/api/student/lessons',
        success: function(data) {
            $('.container').html(data);
        }
    });
});
 