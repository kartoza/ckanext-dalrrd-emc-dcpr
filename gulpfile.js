const path = require("path");
const { src, watch, dest, parallel } = require("gulp");
const less = require("gulp-less");
const if_ = require("gulp-if");
const sourcemaps = require("gulp-sourcemaps");
const rename = require("gulp-rename");

CKAN_BASE_DIR = '/home/appuser/ckan-frontend/public/base'
SOURCE_DIR = __dirname + 'ckanext/dalrrd_emc_dcpr/public/base'

const with_sourcemaps = () => !!process.env.DEBUG;
const renamer = (path) => {
  const variant = process.argv[3];
  if (variant) {
    // convert main/main-rtl into green/green-rtl
    path.basename = path.basename.replace("main", variant.slice(2));
  }
  return path;
};

const build = () =>
  src([
    SOURCE_DIR + "/less/main.less",
  ])
    .pipe(if_(with_sourcemaps(), sourcemaps.init()))
    .pipe(less())
    .pipe(if_(with_sourcemaps(), sourcemaps.write()))
    .pipe(rename(renamer))
    .pipe(dest(SOURCE_DIR + "/css/"));

const watchSource = () =>
  watch(
    SOURCE_DIR + "/less/**/*.less",
    { ignoreInitial: false },
    build
  );

const jquery = () =>
  src(__dirname + "/node_modules/jquery/dist/jquery.js").pipe(
    dest(SOURCE_DIR + "/vendor")
  );

const bootstrap = () =>
  src(__dirname + "/node_modules/bootstrap/dist/**/*").pipe(
    dest(SOURCE_DIR + "/vendor/bootstrap")
  );

const bootstrapLess = () =>
  src(__dirname + "/node_modules/bootstrap/less/**/*").pipe(
    dest(SOURCE_DIR + "/vendor/bootstrap/less")
  );

const moment = () =>
  src(__dirname + "/node_modules/moment/min/moment-with-locales.js").pipe(
    dest(SOURCE_DIR + "/vendor")
  );

const fontAwesomeCss = () =>
  src(__dirname + "/node_modules/font-awesome/css/font-awesome.css").pipe(
    dest(SOURCE_DIR + "/vendor/font-awesome/css")
  );

const fontAwesomeFonts = () =>
  src(__dirname + "/node_modules/font-awesome/fonts/*").pipe(
    dest(SOURCE_DIR + "/vendor/font-awesome/fonts")
  );

const fontAwesomeLess = () =>
  src(__dirname + "/node_modules/font-awesome/less/*").pipe(
    dest(SOURCE_DIR + "/vendor/font-awesome/less")
  );

const jQueryFileUpload = () =>
  src(__dirname + "/node_modules/blueimp-file-upload/js/*.js").pipe(
    dest(SOURCE_DIR + "/vendor/jquery-fileupload/")
  );

const qs = () =>
  src(__dirname + "/node_modules/qs/dist/qs.js").pipe(
    dest(SOURCE_DIR + "/vendor/")
  )

exports.build = build;
exports.watch = watchSource;
exports.updateVendorLibs = parallel(
  jquery,
  bootstrap,
  bootstrapLess,
  moment,
  fontAwesomeCss,
  fontAwesomeFonts,
  fontAwesomeLess,
  jQueryFileUpload,
  qs
);
