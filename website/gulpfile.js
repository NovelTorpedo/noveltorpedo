var gulp = require('gulp');
var webpack = require('webpack-stream');
var sass = require('gulp-sass');
var rename = require('gulp-rename');

// Compile all our JavaScript.
gulp.task('js', function() {
    return gulp.src('resources/js/main.js')
        .pipe(webpack({
            output: {
                filename: 'app.js'
            }
        }))
        .pipe(gulp.dest('static/'));
});

// Compile all of our Sass.
gulp.task('sass', function() {
    return gulp.src('resources/sass/main.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(rename('app.css'))
        .pipe(gulp.dest('static/'));
});

gulp.task('default', ['js', 'sass']);

gulp.task('watch', function() {
    gulp.watch('resources/js/**/*.js', ['js']);
    gulp.watch('resources/sass/**/*.scss', ['sass']);
});
