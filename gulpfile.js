var gulp = require('gulp');
var concat = require('gulp-concat');

gulp.task('scripts', function(){
   return gulp.src('./node_modules/bootstrap/dist/js/bootstrap.bundle.js')
       .pipe(concat('bootstrap.bundle.js'))
       .pipe(gulp.dest('./main/static/assets/js'))
});

gulp.task('default', gulp.series('scripts'));