const path = require("path");
const { src, watch, dest, parallel } = require("gulp");
const less = require("gulp-less");
const if_ = require("gulp-if");
const sourcemaps = require("gulp-sourcemaps");
const rename = require("gulp-rename");

const CKAN_BASE_DIR = '/home/appuser/ckan-frontend/public/base'
const SOURCE_DIR = __dirname + '/ckanext/dalrrd_emc_dcpr/public/base'
const TARGET_DIR = __dirname + '/ckanext/dalrrd_emc_dcpr/assets'

const with_sourcemaps = () => !!process.env.DEBUG;
const renamer = (path) => {
  // const variant = process.argv[3];
  const variant = null;

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
    .pipe(dest(TARGET_DIR + "/css/"));

const watchSource = () =>
  watch(
    SOURCE_DIR + "/less/**/*.less",
    { ignoreInitial: false },
    build
  );

exports.build = build;
exports.watch = watchSource;
