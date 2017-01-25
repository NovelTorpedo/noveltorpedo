var gulp = require('gulp');
var webpack = require('webpack-stream');

gulp.task('default', function() {
    return gulp.src('resources/js/main.js')
        .pipe(webpack())
        .pipe(gulp.dest('static/js.js'));
});
